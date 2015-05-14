
#include "HypothesisStack.h"

namespace Moses
{
HypothesisStack::~HypothesisStack()
{
  // delete all hypos
	RemoveAll();

}

/** Remove hypothesis pointed to by iterator but don't delete the object. */
void HypothesisStack::Detach(const HypothesisStack::iterator &iter)
{
  m_hypos.erase(iter);
}

void HypothesisStack::RemoveAll()
{
	while (m_hypos.begin() != m_hypos.end()) {
    Remove(m_hypos.begin());
  }
}

void HypothesisStack::Remove(const HypothesisStack::iterator &iter)
{
  Hypothesis *h = *iter;
  Detach(iter);
  FREEHYPO(h);
}


}

