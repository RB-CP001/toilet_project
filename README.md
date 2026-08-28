# 🚽 Toilet Bowl 불결을 심판하는 자 — <변좌왕>

> ### **“청결은 선택이 아니다. 정의다.”**

두산로보틱스 **M0609 협동로봇**과 **ROS 2**를 활용한 **자율 변기 청소 로봇 프로젝트**입니다.

변기 상태 확인부터 뚜껑 개방, 세제 도포, 브러시 청소, 헹굼, 마무리까지의 청소 과정을 자동화하고,  
ROS 2 기반 **State Machine**을 통해 전체 프로세스를 관리합니다.

또한 **Qt 기반 HMI Dashboard**를 통해 로봇의 현재 상태와 청소 진행 상황을 실시간으로 확인할 수 있습니다.

---

# 👥 Team

## ⚡ Storm Br8k2r

**B-1 협동1**

| 이름 | 소속 |
|---|---|
| 윤재민 | B-1 협동1 |
| 최성현 | B-1 협동1 |
| 김민서 | B-1 협동1 |
| 고은빈 | B-1 협동1 |

---

# 📌 프로젝트 개요

사람이 직접 수행하기 꺼려지는 반복적이고 비위생적인 변기 청소 작업을  
**협동로봇을 이용하여 자동화**하는 것을 목표로 합니다.

로봇은 변기 상태를 확인한 후 필요한 작업을 순차적으로 수행하며,  
Cleaning Manager가 각 청소 모듈을 관리합니다.

### 전체 청소 과정

```text
👁️ 뚜껑 감지
     │
     ▼
🚪 뚜껑 열기
     │
     ▼
🧴 세제 도포
     │
     ▼
🪥 브러시 청소
     │
     ▼
💧 물 헹굼
     │
     ▼
✅ 마무리

   청소 완료
```

실제 시스템에서는 다음 State로 관리됩니다.

```text
IDLE
  │
  ▼
DETECT_LID      # 뚜껑 감지
  │
  ▼
OPEN_LID        # 뚜껑 열기
  │
  ▼
APPLY_BLEACH    # 세제 도포
  │
  ▼
BRUSH_CLEAN     # 브러시 청소
  │
  ▼
RINSE           # 물 헹굼
  │
  ▼
FINISH          # 마무리
  │
  ▼
DONE            # 청소 완료
```

동작 중 문제가 발생하면 `ERROR` 상태로 전환하여 오류를 처리합니다.

---

# ✨ 주요 기능

- 🤖 Doosan M0609 협동로봇 기반 변기 청소 자동화
- 🧠 State Machine 기반 전체 Cleaning Process 관리
- 👁️ 변기 뚜껑 상태 확인
- 🚪 변기 뚜껑 자동 개방
- 🧴 세제 자동 도포
- 🪥 브러시를 이용한 변기 내부 청소
- 💧 물을 이용한 헹굼
- 🏁 마무리 동작 자동화
- 🖥️ Qt 기반 HMI Dashboard
- 📡 ROS 2 Custom Message 기반 상태 전달
- ⚠️ Robot Safety 및 Error State 관리

---

# 🧹 Cleaning Process

| 단계 | State | 역할 |
|---:|---|---|
| 0 | `IDLE` | 청소 시작 전 대기 |
| 1 | `DETECT_LID` | 변기 뚜껑 상태 확인 |
| 2 | `OPEN_LID` | 필요한 경우 변기 뚜껑 열기 |
| 3 | `APPLY_BLEACH` | 세제를 변기 내부에 도포 |
| 4 | `BRUSH_CLEAN` | 브러시를 이용하여 변기 내부 청소 |
| 5 | `RINSE` | 물을 이용하여 변기 내부 헹굼 |
| 6 | `FINISH` | 청소 종료 및 마무리 동작 |
| 7 | `DONE` | 전체 청소 완료 |
| 8 | `ERROR` | 오류 발생 및 작업 중단 |

---
# 🧠 State Machine & Control Flow

본 시스템은 두 가지 실행 방식을 지원합니다.

1. **AUTO MODE**  
   Cleaning Manager의 State Machine을 통해 전체 청소 과정을 순차적으로 실행합니다.

2. **INDIVIDUAL MODE**  
   HMI에서 원하는 Cleaning Module을 선택하여 개별적으로 실행합니다.

---

## 🔄 전체 제어 구조

```text
                         ┌──────────────┐
                         │    Qt HMI    │
                         └──────┬───────┘
                                │
                     실행 방식 선택
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
         ┌─────────────┐                 ┌─────────────┐
         │  AUTO MODE  │                 │ INDIVIDUAL  │
         │ 전체 청소     │                 │    MODE     │
         └──────┬──────┘                 └──────┬──────┘
                │                               │
                ▼                               │ 
      ┌───────────────────┐                     │
      │ Cleaning Manager  │                     │
      │   State Machine   │                     │
      └─────────┬─────────┘                     │
                │                               │
                ▼                               │
          DETECT_LID ◄──────────────────────────┤
                │                               │
                ▼                               │
           OPEN_LID ◄───────────────────────────┤
                │                               │
                ▼                               │
         APPLY_BLEACH ◄─────────────────────────┤
                │                               │
                ▼                               │
         BRUSH_CLEAN ◄──────────────────────────┤
                │                               │
                ▼                               │
             RINSE ◄────────────────────────────┤
                │                               │
                ▼                               │
            FINISH ◄────────────────────────────┘
                │
                ▼
              DONE
```

> `AUTO MODE`에서는 Cleaning Manager가 State를 순차적으로 전환합니다.  
> `INDIVIDUAL MODE`에서는 전체 State Sequence를 거치지 않고 HMI에서 선택한 Cleaning Module만 실행할 수 있습니다.

---

# 🤖 AUTO MODE — State Machine

전체 자동 청소를 실행하면 `CleaningManager`가 다음 State Machine을 수행합니다.

```text
                         START
                           │
                           ▼
                    ┌─────────────┐
                    │ DETECT_LID  │
                    │  뚜껑 감지    │
                    └──────┬──────┘
                           │
                    Lid Detected?
                     │           │
                    YES          NO
                     │           │
                     ▼           │
                ┌──────────┐     │
                │ OPEN_LID │     │
                │ 뚜껑 열기  │     │
                └────┬─────┘     │
                     │           │
                     └─────┬─────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ APPLY_BLEACH   │
                  │    세제 도포     │
                  └───────┬────────┘
                          │
                          ▼
                  ┌────────────────┐
                  │  BRUSH_CLEAN   │
                  │   브러시 청소    │
                  └───────┬────────┘
                          │
                          ▼
                    ┌───────────┐
                    │   RINSE   │
                    │   물 헹굼  │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │  FINISH   │
                    │   마무리   │
                    └─────┬─────┘
                          │
                          ▼
                     ┌────────┐
                     │  DONE  │
                     └────────┘
```

---

## ⚠️ Safety / Error Transition

각 Cleaning State를 실행하기 전에 Robot Configuration을 확인합니다.

```text
                 Current State
                      │
                      ▼
          ┌────────────────────────┐
          │ Robot Configuration    │
          │        Check           │
          └───────────┬────────────┘
                      │
                 Configuration
                  정상 / 비정상
                  │       │
                  │       └────────────► ERROR
                  ▼
             Module.run()
                  │
             Success?
              │      │
             YES     NO
              │      │
              ▼      └───────────────► ERROR
          Next State
```

따라서 AUTO MODE의 각 State는 기본적으로 다음 구조를 따릅니다.

```text
State 진입
    │
    ▼
Robot Configuration Check
    │
    ├── Fail ───────────────────► ERROR
    │
    ▼
Cleaning Module 실행
    │
    ├── Fail ───────────────────► ERROR
    │
    ▼
다음 State
```

실행 중 Exception이 발생한 경우에도 `ERROR` State로 전환합니다.

```text
Exception
    │
    ▼
┌─────────┐
│  ERROR  │
└─────────┘
    │
    ▼
Cleaning Stop
```

---

# 🎮 INDIVIDUAL MODE — HMI 개별 실행

HMI에서는 전체 Cleaning Sequence와 관계없이 원하는 동작을 선택하여 개별적으로 실행할 수 있습니다.

```text
                     ┌─────────────┐
                     │   Qt HMI    │
                     └──────┬──────┘
                            │
                      동작 선택
                            │
       ┌───────────┬────────┼────────┬───────────┬──────────┐
       │           │        │        │           │          │
       ▼           ▼        ▼        ▼           ▼          ▼
  DETECT_LID   OPEN_LID  APPLY    BRUSH       RINSE      FINISH
                         BLEACH    CLEAN
       │           │        │        │           │          │
       ▼           ▼        ▼        ▼           ▼          ▼
   뚜껑 감지    뚜껑 열기  세제 도포  브러시 청소    물 헹굼     마무리
```

이를 통해 개발 및 테스트 과정에서 전체 Cleaning Process를 실행하지 않고도 특정 단계만 독립적으로 테스트할 수 있습니다.

예를 들어 브러시 청소 동작만 테스트해야 하는 경우:

```text
HMI
 │
 └── BRUSH CLEAN
          │
          ▼
     BrushClean
          │
          ▼
     Robot Motion
```

따라서 세제 도포나 뚜껑 열기 등의 이전 단계를 다시 실행할 필요 없이 필요한 동작만 테스트할 수 있습니다.

---

# 📊 State Transition Table

AUTO MODE의 State 전환 조건은 다음과 같습니다.

| Current State | 조건 | Next State |
|---|---|---|
| `DETECT_LID` | Lid Detected | `OPEN_LID` |
| `DETECT_LID` | Lid Not Detected | `APPLY_BLEACH` |
| `OPEN_LID` | Success | `APPLY_BLEACH` |
| `APPLY_BLEACH` | Success | `BRUSH_CLEAN` |
| `BRUSH_CLEAN` | Success | `RINSE` |
| `RINSE` | Success | `FINISH` |
| `FINISH` | Success | `DONE` |
| Any Cleaning State | Configuration Check Fail | `ERROR` |
| Any Cleaning State | Module Fail | `ERROR` |
| Any Cleaning State | Exception | `ERROR` |

---

## 전체 구조 요약

```text
                         Qt HMI
                           │
              ┌────────────┴────────────┐
              │                         │
         AUTO MODE                INDIVIDUAL MODE
              │                         │
              ▼                         │
       Cleaning Manager                 │
        State Machine                   │
              │                         │
              └────────────┬────────────┘
                           ▼
                  Cleaning Modules
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
      Detect/Open      Bleach/Brush      Rinse/Finish
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                   Doosan ROS 2 API
                           │
                           ▼
                    Doosan M0609
```



### Error 처리

각 State 실행 중 예외 또는 오류가 발생하면:

```text
ANY STATE
    │
    │ Error
    ▼
┌─────────┐
│  ERROR  │
└─────────┘
```

`ERROR` 상태로 전환하여 청소 프로세스를 중단합니다.

---
# ⚙️ System Architecture

전체 시스템은 **Cleaning Manager 기반 자동 청소 모드**와  
**HMI를 통한 개별 동작 제어 모드**로 구성되어 있습니다.

Cleaning Manager는 State Machine을 기반으로 전체 청소 과정을 순차적으로 실행하며,  
HMI에서는 전체 청소 프로세스뿐만 아니라 각 청소 기능을 **개별적으로 호출하여 실행**할 수 있습니다.

```text
┌──────────────────────────────────────────────────────┐
│                       Qt HMI                         │
│                       qt_ui                          │
│                                                      │
│   • 전체 자동 청소 실행                              │
│   • 개별 Cleaning Module 실행                        │
│   • 현재 State / 진행률 모니터링                     │
│   • Robot Status / Message 표시                      │
└───────────────┬──────────────────────┬───────────────┘
                │                      │
        전체 자동 청소              개별 동작 실행
                │                      │
                ▼                      │
┌───────────────────────────────┐      │
│       Cleaning Manager        │      │
│                               │      │
│        State Machine          │      │
│                               │      │
│ • 현재 State 관리             │      │
│ • Robot Configuration Check   │      │
│ • Cleaning Module 순차 실행   │      │
│ • Success / Fail 처리         │      │
│ • Exception → ERROR 처리      │      │
└───────────────┬───────────────┘      │
                │                      │
                │                      │
                ▼                      ▼
┌──────────────────────────────────────────────────────┐
│                  Cleaning Modules                    │
│                                                      │
│   ┌────────────┐       ┌────────────┐                │
│   │ Detect Lid │       │  Open Lid  │                │
│   └────────────┘       └────────────┘                │
│                                                      │
│   ┌──────────────┐     ┌──────────────┐              │
│   │ Apply Bleach │     │ Brush Clean  │              │
│   └──────────────┘     └──────────────┘              │
│                                                      │
│   ┌────────────┐       ┌────────────┐                │
│   │   Rinse    │       │   Finish   │                │
│   └────────────┘       └────────────┘                │
└──────────────────────────┬───────────────────────────┘
                           │
                           │ Doosan ROS 2 API
                           ▼
┌──────────────────────────────────────────────────────┐
│                  Robot Interface                     │
│                                                      │
│                  Doosan M0609                        │
│                  + RG2 Gripper                       │
└──────────────────────────────────────────────────────┘
```

---

# 🎮 HMI Control

Qt 기반 HMI에서는 두 가지 방식으로 로봇 청소 기능을 실행할 수 있습니다.

## 1. 전체 자동 청소

Cleaning Manager를 실행하면 State Machine에 따라 전체 청소 과정이 자동으로 진행됩니다.

```text
START
  │
  ▼
뚜껑 감지
  │
  ├── 뚜껑 열림 ──────────────────┐
  │                               │
  └── 뚜껑 닫힘 → 뚜껑 열기       │
                  │               │
                  └───────────────┤
                                  ▼
                              세제 도포
                                  │
                                  ▼
                             브러시 청소
                                  │
                                  ▼
                                헹굼
                                  │
                                  ▼
                               마무리
                                  │
                                  ▼
                                DONE
```

Cleaning Manager 내부에서는 각 단계 실행 전에 Robot Configuration을 확인하고,  
각 모듈의 실행 결과에 따라 다음 State 또는 `ERROR` State로 전환합니다.

---

## 2. 개별 동작 실행

전체 청소 프로세스를 실행하지 않고도 HMI에서 필요한 청소 기능을 **개별적으로 실행**할 수 있습니다.

```text
                    ┌───────────────┐
                    │    Qt HMI     │
                    └───────┬───────┘
                            │
          ┌─────────┬───────┼───────┬─────────┐
          │         │       │       │         │
          ▼         ▼       ▼       ▼         ▼
      뚜껑 감지   뚜껑 열기  세제 도포  브러시 청소   헹굼
                                                   
                                      + 마무리
```

HMI에서 개별적으로 실행 가능한 기능은 다음과 같습니다.

| 기능 | Cleaning Module | 역할 |
|---|---|---|
| 뚜껑 감지 | `DetectLid` | 현재 변기 뚜껑 상태 확인 |
| 뚜껑 열기 | `OpenLid` | 변기 뚜껑 개방 |
| 세제 도포 | `ApplyBleach` | 변기 내부 세제 도포 |
| 브러시 청소 | `BrushClean` | 변기 내부 브러시 청소 |
| 헹굼 | `Rinse` | 물을 이용한 변기 내부 헹굼 |
| 마무리 | `Finish` | 청소 종료 및 마무리 동작 |

이를 통해 전체 자동 청소뿐만 아니라 **각 단계별 동작 테스트 및 디버깅**도 HMI에서 수행할 수 있습니다.

---

# 🔄 Control Flow

전체 시스템의 제어 흐름은 크게 두 가지입니다.

```text
                    Qt HMI
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
       [전체 자동 실행]      [개별 실행]
             │                 │
             ▼                 │
      Cleaning Manager         │
             │                 │
       State Machine            │
             │                 │
             ▼                 ▼
      ┌────────────────────────────┐
      │      Cleaning Modules      │
      │                            │
      │ Detect Lid   Open Lid      │
      │ Apply Bleach Brush Clean   │
      │ Rinse        Finish        │
      └──────────────┬─────────────┘
                     │
                     ▼
              Doosan ROS 2 API
                     │
                     ▼
               Doosan M0609
```

이 구조를 통해 **자동화된 전체 Cleaning Sequence**와  
**개별 Cleaning Module 제어**를 하나의 HMI에서 통합하여 관리할 수 있습니다.
---

# 📂 Project Structure

```text
src/
│
├── qt_ui/
│   │
│   ├── qt_ui/
│   │   ├── __init__.py
│   │   ├── cobot1_dash_board.py
│   │   ├── cobot1_dash_board.ui
│   │   ├── hmi_main.py
│   │   ├── robot_process.py
│   │   └── ros2_node.py
│   │
│   ├── resource/
│   ├── test/
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
│
├── toilet_cleaning/
│   │
│   ├── toilet_cleaning/
│   │   ├── __init__.py
│   │   ├── apply_bleach.py
│   │   ├── brush_clean.py
│   │   ├── cleaning_manager.py
│   │   ├── detect_lid.py
│   │   ├── finish.py
│   │   ├── open_lid.py
│   │   ├── rinse.py
│   │   └── robot_safety.py
│   │
│   ├── toilet_launch/
│   │   └── toilet_cleaning.launch.py
│   │
│   ├── resource/
│   ├── test/
│   ├── package.xml
│   ├── setup.cfg
│   └── setup.py
│
└── toilet_cleaning_interfaces/
    │
    ├── msg/
    │   └── CleaningStatus.msg
    │
    ├── action/
    ├── CMakeLists.txt
    └── package.xml
```

---

# 📦 Package 설명

## `toilet_cleaning`

실제 변기 청소 동작 및 전체 Cleaning State Machine을 담당하는 핵심 패키지입니다.

| 파일 | 역할 |
|---|---|
| `cleaning_manager.py` | 전체 Cleaning State Machine 관리 |
| `detect_lid.py` | 변기 뚜껑 상태 확인 |
| `open_lid.py` | 변기 뚜껑 개방 |
| `apply_bleach.py` | 세제 도포 |
| `brush_clean.py` | 브러시 청소 |
| `rinse.py` | 변기 내부 헹굼 |
| `finish.py` | 마무리 동작 |
| `robot_safety.py` | 로봇 Safety 관련 처리 |

---

## `qt_ui`

로봇의 상태와 청소 진행 상황을 확인하기 위한 Qt 기반 HMI 패키지입니다.

```text
qt_ui
│
├── hmi_main.py
├── cobot1_dash_board.py
├── cobot1_dash_board.ui
├── robot_process.py
└── ros2_node.py
```

---

## `toilet_cleaning_interfaces`

Cleaning Manager와 HMI 사이의 상태 정보를 전달하기 위한  
ROS 2 Custom Interface 패키지입니다.

```text
toilet_cleaning_interfaces/
└── msg/
    └── CleaningStatus.msg
```

---

# 📡 CleaningStatus Interface

`CleaningStatus.msg`를 이용하여 Cleaning Manager의 현재 상태를 HMI로 전달합니다.

```text
uint8 IDLE=0
uint8 DETECT_LID=1
uint8 OPEN_LID=2
uint8 APPLY_BLEACH=3
uint8 BRUSH_CLEAN=4
uint8 RINSE=5
uint8 FINISH=6
uint8 DONE=7
uint8 ERROR=8

builtin_interfaces/Time stamp

uint8 state
string state_name
float32 progress
bool is_running
string message
```

### 전달 정보

| Field | 설명 |
|---|---|
| `stamp` | 상태가 생성된 시간 |
| `state` | 현재 State 값 |
| `state_name` | 현재 State 이름 |
| `progress` | 전체 청소 진행률 (`0.0 ~ 1.0`) |
| `is_running` | 현재 Cleaning Process 실행 여부 |
| `message` | HMI 및 로그에 표시할 상태 메시지 |

---

# 🛠️ Development Environment

실제 개발 및 실행 환경은 다음과 같습니다.

| 항목 | 환경 |
|---|---|
| **Robot** | Doosan Robotics M0609 |
| **OS** | Ubuntu 24.04.4 LTS (Noble) |
| **ROS** | ROS 2 Jazzy |
| **Language** | Python 3.12.3 |
| **IDE** | Visual Studio Code |
| **HMI** | Qt |
| **Robot Interface** | Doosan Robotics ROS 2 API |

---

# 📦 Dependencies

프로젝트는 ROS 2 Jazzy 환경을 기반으로 하며,  
Doosan M0609 협동로봇 및 Qt 기반 HMI를 사용합니다.

## ROS 2

- ROS 2 Jazzy
- `rclpy`
- `builtin_interfaces`
- ROS 2 Custom Message / Interface

## Doosan Robotics

- Doosan Robotics ROS 2
- `DR_init`
- `DSR_ROBOT2`
- Doosan M0609 Robot Controller
- RG2 Gripper 관련 ROS 2 패키지

## HMI

- Qt
- Python Qt GUI
- ROS 2 ↔ HMI 통신

> 정확한 전체 dependency 및 버전은 각 패키지의 `package.xml`, `setup.py`, `CMakeLists.txt`를 기준으로 확인해야 합니다.

---

# 🚀 실행 방법

## 1️⃣ Doosan Robot Bringup

먼저 Doosan M0609 Robot Controller와 ROS 2를 연결합니다.

새로운 Terminal에서:

```bash
source ~/ws_cobot_pjt/ws_dsr/install/setup.bash

ros2 launch m0609_rg2_bringup bringup.launch.py \
    mode:=real \
    host:=192.168.1.100 \
    port:=12345
```

### 주요 Parameter

| Parameter | Value | 설명 |
|---|---|---|
| `mode` | `real` | 실제 로봇 사용 |
| `host` | `192.168.1.100` | Robot Controller IP |
| `port` | `12345` | Robot Controller Port |

---

## 2️⃣ ROS 2 Node 확인

새로운 Terminal을 실행합니다.

```bash
source ~/toilet_project/toilet_project/install/setup.bash

ros2 node list
```

필요한 ROS 2 Node가 정상적으로 생성되어 있는지 확인합니다.

---

## 3️⃣ Robot Stop Service 확인

```bash
source ~/toilet_project/toilet_project/install/setup.bash

ros2 service list | grep move_stop
```

Robot Stop 관련 Service가 정상적으로 생성되어 있는지 확인합니다.

---

# 🖥️ HMI 실행

새로운 Terminal에서 프로젝트 환경을 Source한 후 HMI를 실행합니다.

```bash
source ~/toilet_project/toilet_project/install/setup.bash

ros2 run qt_ui hmi_main
```

HMI를 통해 다음 정보를 확인할 수 있습니다.

- 현재 Robot 상태
- 현재 Cleaning State
- 전체 청소 진행률
- 작업 진행 메시지
- Error 상태
- Cleaning Process 실행 상태

---

# 🔍 개발 환경 확인

현재 Ubuntu 버전:

```bash
lsb_release -a
```

Python 버전:

```bash
python3 --version
```

ROS 2 Distribution:

```bash
printenv ROS_DISTRO
```

본 프로젝트 개발 환경에서 확인된 결과:

```text
Ubuntu 24.04.4 LTS
Python 3.12.3
ROS_DISTRO=jazzy
```

---

# ⚠️ Safety

본 프로젝트는 **실제 협동로봇을 제어**합니다.

실제 로봇에서 실행하기 전에 다음 사항을 반드시 확인해야 합니다.

- 로봇 주변 작업 공간 확인
- Emergency Stop 사용 가능 상태 확인
- TCP 및 Tool 설정 확인
- 로봇 이동 경로에 사람 또는 장애물이 없는지 확인
- 처음 실행하는 좌표는 낮은 속도로 검증
- Robot Controller와 PC의 네트워크 연결 확인
- 실제 청소 동작 전 각 모듈의 개별 동작 확인

---

# 👑 변좌왕

> ## **불결을 심판하는 자 — <변좌왕>**
>
> **“청결은 선택이 아니다. 정의다.”**

```text
        👁️ 왕좌 감시
             │
             ▼
        🚪 왕좌 개방
             │
             ▼
        🧴 성수 분사
             │
             ▼
      🪥 심판의 브러시
             │
             ▼
        💧 백수정화
             │
             ▼
        👑 왕좌 봉인

          정화 완료.
```

### **오물에게 자비는 없다.**
