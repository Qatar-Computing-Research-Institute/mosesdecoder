#include "TranslationTask.h"
#include "moses/StaticData.h"
#include "moses/Sentence.h"
#include "moses/IOWrapper.h"
#include "moses/TranslationAnalysis.h"
#include "moses/TypeDef.h"
#include "moses/Util.h"
#include "moses/InputType.h"
#include "moses/OutputCollector.h"
#include "moses/Incremental.h"
#include "mbr.h"

#include "moses/Syntax/F2S/RuleMatcherCallback.h"
#include "moses/Syntax/F2S/RuleMatcherHyperTree.h"
#include "moses/Syntax/S2T/Parsers/RecursiveCYKPlusParser/RecursiveCYKPlusParser.h"
#include "moses/Syntax/S2T/Parsers/Scope3Parser/Parser.h"
#include "moses/Syntax/T2S/RuleMatcherSCFG.h"

#include "util/exception.hh"

using namespace std;

namespace Moses
{

std::string const&
TranslationTask
::GetContextString() const
{
  return m_context_string;
}

void
TranslationTask
::SetContextString(std::string const& context)
{
  m_context_string = context;
}



boost::shared_ptr<TranslationTask>
TranslationTask
::create(boost::shared_ptr<InputType> const& source)
{
  boost::shared_ptr<IOWrapper> nix;
  boost::shared_ptr<TranslationTask> ret(new TranslationTask(source, nix));
  ret->m_self = ret;
  ret->m_scope.reset(new ContextScope);
  return ret;
}

boost::shared_ptr<TranslationTask>
TranslationTask
::create(boost::shared_ptr<InputType> const& source,
         boost::shared_ptr<IOWrapper> const& ioWrapper)
{
  boost::shared_ptr<TranslationTask> ret(new TranslationTask(source, ioWrapper));
  ret->m_self = ret;
  ret->m_scope.reset(new ContextScope);
  return ret;
}

TranslationTask
::TranslationTask(boost::shared_ptr<InputType> const& source,
                  boost::shared_ptr<IOWrapper> const& ioWrapper)
  : m_source(source) , m_ioWrapper(ioWrapper)
{ 

}


TranslationTask::~TranslationTask()
{ 

}

  void 
  TranslationTask::
  SetManager(boost::shared_ptr<Moses::BaseManager> const& manager)
  {
    //m_manager=boost::static_pointer_cast(manager);

  }

boost::shared_ptr<BaseManager>
TranslationTask
::SetupManager(SearchAlgorithm algo)
{
  boost::shared_ptr<BaseManager>  manager;
  BaseManager * p_manager;
  StaticData const& staticData = StaticData::Instance();
  if (algo == DefaultSearchAlgorithm) algo = staticData.GetSearchAlgorithm();

  if (!staticData.IsSyntax(algo))
    p_manager = new Manager(this->self()); // phrase-based

  else if (algo == SyntaxF2S || algo == SyntaxT2S)
    { // STSG-based tree-to-string / forest-to-string decoding (ask Phil Williams)
      typedef Syntax::F2S::RuleMatcherCallback Callback;
      typedef Syntax::F2S::RuleMatcherHyperTree<Callback> RuleMatcher;
      p_manager = new Syntax::F2S::Manager<RuleMatcher>(this->self());
    }

  else if (algo == SyntaxS2T)
    { // new-style string-to-tree decoding (ask Phil Williams)
      S2TParsingAlgorithm algorithm = staticData.GetS2TParsingAlgorithm();
      if (algorithm == RecursiveCYKPlus)
	{
	  typedef Syntax::S2T::EagerParserCallback Callback;
	  typedef Syntax::S2T::RecursiveCYKPlusParser<Callback> Parser;
	  p_manager = new Syntax::S2T::Manager<Parser>(this->self());
	}
      else if (algorithm == Scope3)
	{
	  typedef Syntax::S2T::StandardParserCallback Callback;
	  typedef Syntax::S2T::Scope3Parser<Callback> Parser;
	  p_manager = new Syntax::S2T::Manager<Parser>(this->self());
	}
      else UTIL_THROW2("ERROR: unhandled S2T parsing algorithm");
    }

  else if (algo == SyntaxT2S_SCFG)
    { // SCFG-based tree-to-string decoding (ask Phil Williams)
      typedef Syntax::F2S::RuleMatcherCallback Callback;
      typedef Syntax::T2S::RuleMatcherSCFG<Callback> RuleMatcher;
      p_manager =new Syntax::T2S::Manager<RuleMatcher>(this->self());
    }

  else if (algo == ChartIncremental) // Ken's incremental decoding
    p_manager =new Incremental::Manager(this->self());

  else // original SCFG manager
    p_manager = new ChartManager(this->self());

  manager.reset(p_manager);
  return manager;
}

void TranslationTask
::Continue(boost::shared_ptr<BaseManager> const & p_manager)
{
  // shorthand for "global data"
  const size_t translationId = m_source->GetTranslationId();
  Timer translationTime;
  translationTime.start();

  std::cerr<<"Got to here 1"<<endl;
  boost::shared_ptr<Manager> const & manager=boost::static_pointer_cast<Manager>(p_manager);
  
  std::cerr<<"Got to here 2"<<endl;
  manager->ContinueDecode();

    // new: stop here if m_ioWrapper is NULL. This means that the
    // owner of the TranslationTask will take care of the output
    // oh, and by the way, all the output should be handled by the
    // output wrapper along the lines of *m_iwWrapper << *manager;
    // Just sayin' ...
    std::cerr<<"Got to here 3"<<endl;
    if (m_ioWrapper == NULL) return;
    // we are done with search, let's look what we got
    OutputCollector* ocoll;
    Timer additionalReportingTime;
    additionalReportingTime.start();

    boost::shared_ptr<IOWrapper> const& io = m_ioWrapper;
    manager->OutputBest(io->GetSingleBestOutputCollector());

    // output word graph
    manager->OutputWordGraph(io->GetWordGraphCollector());

    // output search graph
    manager->OutputSearchGraph(io->GetSearchGraphOutputCollector());

    // ???
    manager->OutputSearchGraphSLF();

    // Output search graph in hypergraph format for Kenneth Heafield's
    // lazy hypergraph decoder; writes to stderr
    manager->OutputSearchGraphHypergraph();

    additionalReportingTime.stop();

    additionalReportingTime.start();

    // output n-best list
    manager->OutputNBest(io->GetNBestOutputCollector());

    //lattice samples
    manager->OutputLatticeSamples(io->GetLatticeSamplesCollector());

    // detailed translation reporting
    ocoll = io->GetDetailedTranslationCollector();
    manager->OutputDetailedTranslationReport(ocoll);

    ocoll = io->GetDetailTreeFragmentsOutputCollector();
    manager->OutputDetailedTreeFragmentsTranslationReport(ocoll);

    //list of unknown words
    manager->OutputUnknowns(io->GetUnknownsCollector());

    manager->OutputAlignment(io->GetAlignmentInfoCollector());

    // report additional statistics
    manager->CalcDecoderStatistics();
    VERBOSE(1, "Line " << translationId << ": Additional reporting took "
            << additionalReportingTime << " seconds total" << endl);
    VERBOSE(1, "Line " << translationId << ": Translation took "
            << translationTime << " seconds total" << endl);
    IFVERBOSE(2) {
      PrintUserTime("Sentence Decoding Time:");
    }

}
void TranslationTask::Run()
{
  boost::shared_ptr<BaseManager> dummy= RunWithManager();
}

boost::shared_ptr<BaseManager>
TranslationTask::RunWithManager()
{
  UTIL_THROW_IF2(!m_source || !m_ioWrapper,
		 "Base Instances of TranslationTask must be initialized with"
		 << " input and iowrapper.");


  // shorthand for "global data"
  const size_t translationId = m_source->GetTranslationId();

  // report wall time spent on translation
  Timer translationTime;
  translationTime.start();

  // report thread number
#if defined(WITH_THREADS) && defined(BOOST_HAS_PTHREADS)
  VERBOSE(2, "Translating line " << translationId << "  in thread id " << pthread_self() << endl);
#endif


  // execute the translation
  // note: this executes the search, resulting in a search graph
  //       we still need to apply the decision rule (MAP, MBR, ...)
  Timer initTime;
  initTime.start();

 
  boost::shared_ptr<BaseManager> manager=SetupManager();

  VERBOSE(1, "Line " << translationId << ": Initialize search took "
	  << initTime << " seconds total" << endl);

  manager->Decode();

  // new: stop here if m_ioWrapper is NULL. This means that the
  // owner of the TranslationTask will take care of the output
  // oh, and by the way, all the output should be handled by the
  // output wrapper along the lines of *m_iwWrapper << *manager;
  // Just sayin' ...
  if (m_ioWrapper == NULL) return manager;
  // we are done with search, let's look what we got
  OutputCollector* ocoll;
  Timer additionalReportingTime;
  additionalReportingTime.start();

  boost::shared_ptr<IOWrapper> const& io = m_ioWrapper;
  manager->OutputBest(io->GetSingleBestOutputCollector());

  // output word graph
  manager->OutputWordGraph(io->GetWordGraphCollector());

  // output search graph
  manager->OutputSearchGraph(io->GetSearchGraphOutputCollector());

  // ???
  manager->OutputSearchGraphSLF();

  // Output search graph in hypergraph format for Kenneth Heafield's
  // lazy hypergraph decoder; writes to stderr
  manager->OutputSearchGraphHypergraph();

  additionalReportingTime.stop();

  additionalReportingTime.start();

  // output n-best list
  manager->OutputNBest(io->GetNBestOutputCollector());

  //lattice samples
  manager->OutputLatticeSamples(io->GetLatticeSamplesCollector());

  // detailed translation reporting
  ocoll = io->GetDetailedTranslationCollector();
  manager->OutputDetailedTranslationReport(ocoll);

  ocoll = io->GetDetailTreeFragmentsOutputCollector();
  manager->OutputDetailedTreeFragmentsTranslationReport(ocoll);

  //list of unknown words
  manager->OutputUnknowns(io->GetUnknownsCollector());

  manager->OutputAlignment(io->GetAlignmentInfoCollector());

  // report additional statistics
  manager->CalcDecoderStatistics();
  VERBOSE(1, "Line " << translationId << ": Additional reporting took "
	  << additionalReportingTime << " seconds total" << endl);
  VERBOSE(1, "Line " << translationId << ": Translation took "
	  << translationTime << " seconds total" << endl);
  IFVERBOSE(2) {
    PrintUserTime("Sentence Decoding Time:");
  }
  return boost::shared_ptr<BaseManager>(manager);
}

}
