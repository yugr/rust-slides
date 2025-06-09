// Simple tool to count loops with bounds checks in .bc files

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

static cl::list<std::string> InputFilenames(cl::Positional,
                                            cl::desc("[input bitcode]..."));

namespace {

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

  bool isBoundsCheckPanic(const Instruction &I) const {
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

  bool canPanic(const BasicBlock &BB) const {
    return any_of(BB.instructionsWithoutDebug(),
                  [this](auto &I) { return isBoundsCheckPanic(I); });
  }

  bool hasBoundsCheck(const BasicBlock &BB) const {
    return any_of(successors(&BB),
                  [this](auto *Succ) { return canPanic(*Succ); });
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

    auto &OuterProxy = LAM.getResult<FunctionAnalysisManagerLoopProxy>(L, AR);
    if (auto *BFI = OuterProxy.getCachedResult<BlockFrequencyAnalysis>(*F)) {
      const BranchProbability ColdProb(5, 100);
      auto LoopFreq = BFI->getBlockFreq(Header);
      auto EntryFreq = BFI->getBlockFreq(&F->getEntryBlock());
      if (LoopFreq < EntryFreq * ColdProb) {
        LLVM_DEBUG(errs() << "Skipped cold loop\n");
        return PA;
      }
    }

    if (any_of(L.getBlocks(),
               [this](auto *BB) { return hasBoundsCheck(*BB); })) {
      outs() << "BC in loop\n";
    } else {
      outs() << "No BC in loop\n";
    }

    return PA;
  }
};

Regex PanicCounterPass::PanicName("_ZN4core9panicking"
                                  "|_ZN4core5slice.*_fail"
                                  "|_ZN4core6option13expect_failed"
                                  "|_ZN4core6option13unwrap_failed");

} // namespace

static ExitOnError ExitOnErr;

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
  MPM = PB.buildO0DefaultPipeline(OptimizationLevel::O0);
  MPM.addPass(createModuleToFunctionPassAdaptor(
      createFunctionToLoopPassAdaptor(PanicCounterPass())));

  MPM.run(M, MAM);
}

int libmain(int argc, char **argv) {
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
