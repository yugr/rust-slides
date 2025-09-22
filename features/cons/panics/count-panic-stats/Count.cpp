// Simple tool to count panic/unwind stats in .bc files

#include "llvm/Analysis/PostDominators.h"
#include "llvm/Bitcode/BitcodeReader.h"
#include "llvm/IR/DiagnosticInfo.h"
#include "llvm/IR/DiagnosticPrinter.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/Type.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Error.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Support/FormattedStream.h"
#include "llvm/Support/InitLLVM.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/Regex.h"
#include "llvm/Support/WithColor.h"
#include <numeric>
#include <system_error>

#define DEBUG_TYPE "count-panics"

using namespace llvm;

namespace {

cl::list<std::string> InputFilenames(cl::Positional,
                                     cl::desc("[input bitcode]..."));

struct LLVMDisDiagnosticHandler : public DiagnosticHandler {
  char *Prefix;
  LLVMDisDiagnosticHandler(char *PrefixPtr) : Prefix(PrefixPtr) {}
  bool handleDiagnostics(const DiagnosticInfo &DI) override {
    raw_ostream &OS = errs();
    OS << Prefix << ": ";
    switch (DI.getSeverity()) {
    case DS_Error:
      WithColor::error(OS);
      break;
    case DS_Warning:
      WithColor::warning(OS);
      break;
    case DS_Remark:
      OS << "remark: ";
      break;
    case DS_Note:
      WithColor::note(OS);
      break;
    }

    DiagnosticPrinterRawOStream DP(OS);
    DI.print(DP);
    OS << '\n';

    if (DI.getSeverity() == DS_Error)
      exit(1);
    return true;
  }
};

class PanicCounterPass : public PassInfoMixin<PanicCounterPass> {
  PostDominatorTree *PDT = nullptr;

  bool isPanic(const Instruction &I) const {
    auto *CI = dyn_cast<CallInst>(&I);
    if (!CI)
      return false;

    auto *F = CI->getCalledFunction();
    if (!F)
      return false;

    auto Name = F->getName();
    return Name.starts_with("_ZN4core9panicking") ||
           Name.starts_with("_ZN4core5slice5index") ||
           Name.starts_with("_ZN4core6option13unwrap_failed") ||
           Name.starts_with("_ZN4core6option13expect_failed") ||
           Name.starts_with("_ZN4core6result13unwrap_failed") ||
           Name.starts_with("_ZN4core6result13unwrap_failed") ||
           Name.starts_with("_ZN4core3str19slice_error_fail");
  }

  std::set<BasicBlock *> addPostdoms(const std::set<BasicBlock *> &Roots) {
    std::set<BasicBlock *> Result;

    for (auto *BB : Roots) {
      SmallVector<BasicBlock *> PostDomBBs;
      PDT->getDescendants(BB, PostDomBBs);
      Result.insert(PostDomBBs.begin(), PostDomBBs.end());
    }

    return Result;
  }

  unsigned countInsns(const std::set<BasicBlock *> &Blocks) const {
    return std::accumulate(Blocks.begin(), Blocks.end(), 0u,
                           [](unsigned A, auto *BB) { return A + BB->size(); });
  }

public:
  PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM) {
    PDT = &AM.getResult<PostDominatorTreeAnalysis>(F);

    unsigned NumInsns = 0;
    for (auto &I : instructions(F))
      ++NumInsns;

    const auto NumBBs = F.size();

    // Panicking blocks

    std::set<BasicBlock *> InitialPanicBBs;
    unsigned NumPanics = 0;

    for (auto &I : instructions(&F)) {
      if (isPanic(I)) {
        auto *BB = I.getParent();
        InitialPanicBBs.insert(BB);
        ++NumPanics;
      }
    }

    const std::set<BasicBlock *> PanicBBs = addPostdoms(InitialPanicBBs);
    const unsigned NumPanicHandlingInsns = countInsns(PanicBBs);

    // Landing pads

    std::set<BasicBlock *> LPads;
    unsigned NumInvokes = 0;
    unsigned NumCalls = 0;

    for (auto &I : instructions(&F)) {
      if (auto *Invoke = dyn_cast<InvokeInst>(&I)) {
        LPads.insert(Invoke->getUnwindDest());
        ++NumInvokes;
      } else if (auto *Call = dyn_cast<CallInst>(&I)) {
        NumCalls += Call->getIntrinsicID() != Intrinsic::not_intrinsic;
      }
    }

    const std::set<BasicBlock *> UnwindBBs = addPostdoms(LPads);
    const unsigned NumUnwindInsns = countInsns(UnwindBBs);

    // Print results

    auto Name = F.getName();

    outs() << Name << " all insns: " << NumInsns << "\n";
    outs() << Name << " calls: " << NumCalls << "\n";
    outs() << Name << " invokes: " << NumCalls << "\n";
    outs() << Name << " panics: " << NumPanics << "\n";
    outs() << Name << " panic handling insns: " << NumPanicHandlingInsns
           << "\n";
    outs() << Name << " unwind insns: " << NumUnwindInsns << "\n";

    outs() << Name << " all blocks: " << F.size() << "\n";
    outs() << Name << " panic handling blocks: " << PanicBBs.size() << "\n";
    outs() << Name << " unwind blocks: " << UnwindBBs.size() << "\n";

    return PreservedAnalyses::all();
  }
};

ExitOnError ExitOnErr;

void processModule(Module &M) {
  LoopAnalysisManager LAM;
  FunctionAnalysisManager FAM;
  CGSCCAnalysisManager CGAM;
  ModuleAnalysisManager MAM;

  PassInstrumentationCallbacks PIC;
  PassBuilder PB(nullptr, PipelineTuningOptions(), std::nullopt, &PIC);

  PB.registerModuleAnalyses(MAM);
  PB.registerCGSCCAnalyses(CGAM);
  PB.registerFunctionAnalyses(FAM);
  PB.registerLoopAnalyses(LAM);
  PB.crossRegisterProxies(LAM, FAM, CGAM, MAM);

  ModulePassManager MPM;
  MPM.addPass(createModuleToFunctionPassAdaptor(PanicCounterPass()));

  MPM.run(M, MAM);
}

} // namespace

int main(int argc, char **argv) {
  InitLLVM X(argc, argv);

  ExitOnErr.setBanner(std::string(argv[0]) + ": error: ");

  cl::ParseCommandLineOptions(argc, argv, "llvm .bc analyzer\n");

  if (InputFilenames.size() < 1) {
    InputFilenames.push_back("-");
  }

  for (const auto &InputFilename : InputFilenames) {
    // Use a fresh context for each input to avoid state
    // cross-contamination across inputs (e.g. type name collisions).
    LLVMContext Context;
    Context.setDiagnosticHandler(
        std::make_unique<LLVMDisDiagnosticHandler>(argv[0]));

    ErrorOr<std::unique_ptr<MemoryBuffer>> BufferOrErr =
        MemoryBuffer::getFileOrSTDIN(InputFilename);
    if (std::error_code EC = BufferOrErr.getError()) {
      WithColor::error() << InputFilename << ": " << EC.message() << '\n';
      return 1;
    }
    std::unique_ptr<MemoryBuffer> MB = std::move(BufferOrErr.get());

    BitcodeFileContents IF = ExitOnErr(llvm::getBitcodeFileContents(*MB));

    const size_t N = IF.Mods.size();

    for (size_t I = 0; I < N; ++I) {
      BitcodeModule MB = IF.Mods[I];

      auto M = ExitOnErr(MB.getLazyModule(
          Context, /*MaterializeMetadata*/ false, /*SetImporting*/ false));
      ExitOnErr(M->materializeAll());

      processModule(*M);
    }
  }

  return 0;
}
