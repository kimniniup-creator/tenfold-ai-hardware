#pragma once
#include <stdint.h>
struct ReadingState {
  enum Event { None, Pet, Mark, Mode };
  struct Marker { uint32_t session, elapsed, interaction, mode, ordinal; };
  uint32_t version=1, interactions=0, session=0, markCount=0;
  Marker marks[16]{};
  bool quiet=false;
  uint8_t mode=0;
};
struct ReadingInput {
  bool a=false,b=false;
  uint32_t bSince=0;
  ReadingState::Event update(ReadingState& state,bool nextA,bool nextB,uint32_t now,uint32_t elapsed){
    auto event=ReadingState::None;
    if(nextA&&!a){if(state.interactions<UINT32_MAX)++state.interactions;event=ReadingState::Pet;}
    if(nextB&&!b)bSince=now;
    if(!nextB&&b){
      if(now-bSince>=700){state.mode=(state.mode+1)%4;event=ReadingState::Mode;}
      else {state.marks[state.markCount%16]={state.session,elapsed,state.interactions,state.mode,state.markCount};if(state.markCount<UINT32_MAX)++state.markCount;event=ReadingState::Mark;}
    }
    a=nextA;b=nextB;return event;
  }
};
inline bool readingSelfTest(){
 ReadingState s;ReadingInput i;s.session=7;
 if(i.update(s,true,false,0,0)!=ReadingState::Pet)return false;
 i.update(s,true,false,10000,10000);if(s.interactions!=1)return false;
 i.update(s,false,false,10001,10001);i.update(s,true,false,10002,10002);if(s.interactions!=2)return false;
 i.update(s,false,true,11000,11000);if(s.markCount)return false;
 if(i.update(s,false,false,11699,11699)!=ReadingState::Mark||s.markCount!=1)return false;
 i.update(s,false,true,12000,12000);if(i.update(s,false,false,12700,12700)!=ReadingState::Mode||s.markCount!=1||s.mode!=1)return false;
 i.update(s,false,true,UINT32_MAX-300,0);if(i.update(s,false,false,500,0)!=ReadingState::Mode||s.mode!=2)return false;
 return s.marks[0].session==7&&s.marks[0].interaction==2;
}
