#include "SpanLengthEstimator.h"
#include <vector>
#include <map>
#include "util/check.hh"
#include "StaticData.h"
#include "TypeDef.h"

using namespace std;
namespace Moses
{

void SpanLengthEstimator::AddSourceSpanScore(unsigned sourceSpanLength, float score)
{
  m_sourceScores.insert(make_pair(sourceSpanLength, score));
}

void SpanLengthEstimator::AddTargetSpanScore(unsigned targetSpanLength, float score)
{
    m_targetScores.insert(make_pair(targetSpanLength, score));
}

//Just in case we need the sum of both scores (probably never...)
//float SpanLengthEstimator::GetScoreBySpanLengths(unsigned sourceSpanLength, unsigned targetSpanLength) const
//{
//  return FetchScoreFromMap(m_sourceScores, sourceSpanLength) + FetchScoreFromMap(m_targetScores, targetSpanLength);
//}

float SpanLengthEstimator::GetScoreBySourceSpanLength(unsigned sourceSpanLength) const
{
  bool useGaussian = StaticData::Instance().GetParam("gaussian-span-length-score").size() > 0;
  if (useGaussian)
    return FetchGaussianScoreFromMap(m_sourceScores, sourceSpanLength);
  else
    return FetchScoreFromMap(m_sourceScores, sourceSpanLength);
}

float SpanLengthEstimator::GetScoreByTargetSpanLength(unsigned targetSpanLength) const
{
  bool useGaussian = StaticData::Instance().GetParam("gaussian-span-length-score").size() > 0;
  if (useGaussian)
    return FetchGaussianScoreFromMap(m_targetScores, targetSpanLength);
  else
    return FetchScoreFromMap(m_targetScores, targetSpanLength);
}

float SpanLengthEstimator::FetchScoreFromMap(const TLengthToScoreMap &lengthToScoreMap, unsigned spanLength)
{
  if (lengthToScoreMap.empty())
    return 0.0;
  TLengthToScoreMap::const_iterator iter = lengthToScoreMap.find(spanLength);
  if (iter == lengthToScoreMap.end())
    return LOWEST_SCORE;
  else
    return iter->second;
}
  
float SpanLengthEstimatorCollection::GetScoreBySourceSpanLength(
  unsigned nonTerminalIndex,
  unsigned sourceSpanLength) const
{
  if (empty())
    return 0.0f;
  CHECK(size() > size_t(nonTerminalIndex));
  return (*this)[nonTerminalIndex].GetScoreBySourceSpanLength(sourceSpanLength);
}
  
float SpanLengthEstimatorCollection::GetScoreByTargetSpanLength(
  unsigned nonTerminalIndex,
  unsigned targetSpanLength) const
{
  if (empty())
    return 0.0f;
  CHECK(size() > size_t(nonTerminalIndex));
  return (*this)[nonTerminalIndex].GetScoreByTargetSpanLength(targetSpanLength);
}

float SpanLengthEstimator::FetchGaussianScoreFromMap(const TLengthToScoreMap& lengthToScoreMap, unsigned spanLength)
{
  
}

} // namespace