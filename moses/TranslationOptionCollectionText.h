// $Id$

/***********************************************************************
Moses - factored phrase-based language decoder
Copyright (C) 2006 University of Edinburgh

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
***********************************************************************/

#ifndef moses_TranslationOptionCollectionText_h
#define moses_TranslationOptionCollectionText_h

#include "TranslationOptionCollection.h"
#include "InputPath.h"
#include <map>
#include <vector>

namespace Moses
{

class Sentence;

/** Holds all translation options, for all spans, of a particular sentence input
 * Inherited from TranslationOptionCollection.
 */
class TranslationOptionCollectionText : public TranslationOptionCollection
{
public:
  typedef std::vector< std::vector<InputPath*> > InputPathMatrix;

protected:
  InputPathMatrix	m_inputPathMatrix; /*< contains translation options */

  InputPath &GetInputPath(size_t startPos, size_t endPos);

public:

  TranslationOptionCollectionText(ttasksptr const& ttask, Sentence const& input, size_t maxNoTransOptPerCoverage, float translationOptionThreshold);

  void Init(Sentence const& input);
  // PG: For stream decoding
  void ReInit();

  //! For stream decoding, expand the path matrix for newly added input
  void ExpandInputPathMatrix();


  bool HasXmlOptionsOverlappingRange(size_t startPosition, size_t endPosition) const;
  bool ViolatesXmlOptionsConstraint(size_t startPosition, size_t endPosition, TranslationOption *transOpt) const;
  void CreateXmlOptionsForRange(size_t startPosition, size_t endPosition);

  void CreateTranslationOptions();

  //* sv: for stream decoding - find translation options for source sequences including new word(s)
  void ExpandTranslationOptions();


  bool CreateTranslationOptionsForRange(const DecodeGraph &decodeStepList
                                        , size_t startPosition
                                        , size_t endPosition
                                        , bool adhereTableLimit
                                        , size_t graphInd);

  void ProcessUnknownWord(size_t sourcePos);

};

}

#endif

