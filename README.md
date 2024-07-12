# 자동 훈련기능을 포함한 PCB결함검사 프로그램
---

![DALLE2024-05-2415 30 33-AverysimplecoverimageforaprojectaboutPCBPrintedCircuitBoarddefectinspectionincorporatingtheconceptofchanginglightingconditions-ezgif com-webp-to-jpg-converter](https://github.com/user-attachments/assets/80975705-d0af-401c-a2c3-85903f0d1269)
* 시연 동영상 링크 :
* 노션 : 

## 프로젝트 소개
---
* 인공지능 모델을 훈련하고 강화시키기 위해서는 대량의 라벨링과 꾸준한 업데이트가 필요하다.
* 수작업으로 하기에는 시간과 비용이 많이 발생하는 문제가 있다.
* 자동 라벨링 기능을 구현하여 신속하고 정확한 데이터 라벨링, 그리고 지속적인 개선이 가능하다.

## 팀원 구성
---
<table>
  <tbody>
      <td align="center"><a href=""><img src="" width="100px;" alt=""/><br /><sub><b>정재현 </b></sub></a><br /></td>
      <td align="center"><a href=""><img src="" width="100px;" alt=""/><br /><sub><b>윤석현 </b></sub></a><br /></td>
      <td align="center"><a href=""><img src="" width="100px;" alt=""/><br /><sub><b>성재민 </b></sub></a><br /></td>
    </tr>
  </tbody>
</table>

## 개발 환경
---
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/PyQT5-41CD52?style=for-the-badge&logo=Qt&logoColor=white">
<img src="https://img.shields.io/badge/Arduino-00878F?style=for-the-badge&logo=Arduino&logoColor=white">
<img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white">
<img src="https://img.shields.io/badge/AutoCAD-E51050?style=for-the-badge&logo=AutoCAD&logoColor=white">  

![image](https://github.com/user-attachments/assets/1e662660-771e-4d5b-9df5-759df3647a31)

## 역할 분담
---
🐬 정재현
* 강화학습을 활용한자동 라벨링 기능 구현
* PCB 결함감지 모델 제작
* 코드 통합

😎 윤석현
* AutoCAD를 활용하여 컨베이어 벨트 설계도 제작
* 아두이노 환경구축, 시리얼 통신

👻 성재민
* UI제작
* DB 설계

## 작업 관리
---
* Notion 팀 프로젝트 워크스페이스를 생성하여 금요일마다 회의를 진행하고 각종 진행상황 공유
* GitHub엔 업데이트 된 코드 등록

## 신경 쓴 부분
---
- 관리자가 사용하는 프로그램이라고 생각하고 제작
- 초기에 최소한의 라벨링만 진행한다
- 그 후로 인식되는 결함의 좌표를 자동으로 따 데이터를 축적시키고 UI에서 업데이트 버튼을 눌러 축적한 데이터를 포함해 훈련을 진행함으로써 인식률을 지속적으로 향상시킨다.
- 3D프린터를 활용해서 직접 컨베이어벨트를 제작해서 프로젝트를 진행했다.
  
## 더 나아갈 점
---
- 조도센서로 빛을 감지해 LED를 키는 부분을 opencv rgb값인식을 통해 주변 밝기를 인식시켜 led밝기를 조절하면 더 좋을거 같다.
- 훈련을 진행할때 항상 전체사진으로 진행하는데 새로 생긴 데이터만 추가하는 방식으로 바꾸면 더 효율적일 거 같다.
- 3D프린터로 제품을 받고 보니 초기 계획대로 진행하는데 제한이 생겼다. -> 초기에 설계할때 조원끼리 피드백하기
- LED의 빛이 한곳에 집중되는 현상때문에 역광 발생 -> LED위치를 변경하거나 빛을 퍼지게 해야할 거 같다.
- 현재 PC로만 접근할 수 있기때문에 관리자 입장에서 모바일로도 접근이 가능하다면 더욱 좋을 거 같다.
