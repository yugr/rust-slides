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

class CounterPass : public PassInfoMixin<CounterPass> {
public:
  CounterPass() {}

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

    unsigned NumStores = 0;
    unsigned NumMemsets = 0;

    for (auto *BB : L.getBlocks()) {
      for (auto &I : *BB) {
        NumStores += isa<StoreInst>(I);
        NumMemsets += isa<MemSetInst>(I);
      }
    }

    outs() << "Loop stats: " << NumStores << " stores, "
           << NumMemsets << " memsets\n";

    return PA;
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
  MPM.addPass(createModuleToFunctionPassAdaptor(
      RequireAnalysisPass<BlockFrequencyAnalysis, Function>()));
  MPM.addPass(createModuleToFunctionPassAdaptor(createFunctionToLoopPassAdaptor(
      CounterPass(), /*UseMemorySSA*/ false, /*UseBlockFrequencyInfo*/ true)));

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
