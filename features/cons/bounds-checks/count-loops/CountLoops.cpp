// Simple tool to count loops with panicking checks in .bc files

#include "llvm/Analysis/BlockFrequencyInfo.h"
#include "llvm/Analysis/LoopAnalysisManager.h"
#include "llvm/Bitcode/BitcodeReader.h"
#include "llvm/IR/DiagnosticInfo.h"
#include "llvm/IR/DiagnosticPrinter.h"
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
#include "llvm/Transforms/Scalar/LoopPassManager.h"
#include <system_error>

#define DEBUG_TYPE "count-panics"

using namespace llvm;

namespace {

cl::opt<bool> SkipColds("skip-colds", cl::desc("Skip cold loops"), cl::Hidden);

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
  static Regex PanicName;

  bool isPanic(const Instruction &I) const {
    auto *CI = dyn_cast<CallInst>(&I);
    if (!CI)
      return false;

    auto *F = CI->getCalledFunction();
    if (!F)
      return false;

    if (!PanicName.match(F->getName()))
      return false;

    LLVM_DEBUG(errs() << "Found panic: " << I << "\n");

    return true;
  }

  bool doesPanic(const BasicBlock &BB) const {
    // TODO: post-dominated by panic ?
    return any_of(BB.instructionsWithoutDebug(),
                  [this](auto &I) { return isPanic(I); });
  }

  bool mayPanic(const BasicBlock &BB) const {
    return any_of(successors(&BB),
                  [this](auto *Succ) { return doesPanic(*Succ); });
  }

public:
  PanicCounterPass() {}

  PreservedAnalyses run(Loop &L, LoopAnalysisManager &LAM,
                        LoopStandardAnalysisResults &AR, LPMUpdater &U) {
    const auto PA = PreservedAnalyses::all();

    if (!L.isInnermost())
      return PA;

    auto *Header = L.getHeader();
    auto *F = Header->getParent();

    if (SkipColds) {
      assert(AR.BFI && "Missing BFI");

      auto LoopFreq = AR.BFI->getBlockFreq(Header);
      auto EntryFreq = AR.BFI->getBlockFreq(&F->getEntryBlock());
      LLVM_DEBUG(auto Ratio =
                     (double)LoopFreq.getFrequency() / EntryFreq.getFrequency();
                 errs() << "Loop " << L.getName() << ": " << Ratio << "\n";);
      if (LoopFreq <= EntryFreq) {
        LLVM_DEBUG(errs() << "Skipped cold loop\n");
        return PA;
      }
    }

    if (any_of(L.getBlocks(), [this](auto *BB) { return mayPanic(*BB); })) {
      outs() << "Loop may panic\n";
    } else {
      outs() << "Loop may NOT panic\n";
    }

    return PA;
  }
};

// See analysis.md for explanation

Regex PanicCounterPass::PanicName(
    // Explicit panics
    "_ZN4core9panicking5panic17"
    "|_ZN4core9panicking9panic_fmt17"
    "|_ZN4core9panicking14panic_nounwind"
    "|_ZN4core9panicking18panic_nounwind_fmt"
    "|_ZN3std9panicking11begin_panic17"
    // Unwraps
    "|_ZN4core9panicking13assert_failed"
    "|_ZN4core6option13expect_failed"
    "|_ZN4core6option13unwrap_failed"
    // Codegen checks
    "|_ZN4core9panicking18panic_bounds_check"
    "|_ZN4core9panicking30panic_null_pointer_dereference"
    "|_ZN4core9panicking36panic_misaligned_pointer_dereference"
    "|_ZN4core5slice.*_fail");


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
  MPM.addPass(createModuleToFunctionPassAdaptor(
      RequireAnalysisPass<BlockFrequencyAnalysis, Function>()));
  MPM.addPass(createModuleToFunctionPassAdaptor(createFunctionToLoopPassAdaptor(
      PanicCounterPass(), /*UseMemorySSA*/ false,
      /*UseBlockFrequencyInfo*/ true)));

  // Fake profile data because otherwise AR.BFI will not be set...
  for (auto &F : M)
    F.setEntryCount(Function::ProfileCount(100, Function::PCT_Real));

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
