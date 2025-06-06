# 🎨 Smart MES-ERP V1.1 Mockup

## 📊 품질관리 모듈 화면 구성

### 1. 메인 대시보드 추가 요소
```
┌─────────────────────────────────────────────────────────┐
│ 🏭 Smart MES-ERP V1.1                    👤 Guest       │
├─────────────────────────────────────────────────────────┤
│ 대시보드 | MES | 재고 | 구매 | 영업 | [품질] | 회계 | 설정 │
└─────────────────────────────────────────────────────────┘

[시스템 상태 카드]
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 🔍 오늘 검사  │ ✅ 합격률     │ ⚠️ 불량률     │ 🔧 교정예정   │
│    25건      │   98.5%      │   1.5%       │    3대       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

### 2. 품질관리 메인 화면
```
┌─────────────────────────────────────────────────────────┐
│ 📋 품질관리 시스템                                        │
├─────────────────────────────────────────────────────────┤
│ [검사 관리] [불량 관리] [SPC] [성적서] [분석] [설정]      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 검사 현황 요약                                         │
│ ┌────────┬────────┬────────┬────────┐                   │
│ │오늘검사 │ 합격률  │ 불량률  │교정예정│                   │
│ │  25건  │ 98.5%  │ 1.5%   │  3대   │                   │
│ └────────┴────────┴────────┴────────┘                   │
│                                                          │
│ 📈 검사 관리                    [+ 검사 등록] [⚙️ 기준]    │
│ ┌─────────────────────────────────────────────────┐     │
│ │ [입고검사] [공정검사] [출하검사]                    │     │
│ ├─────────────────────────────────────────────────┤     │
│ │ 검사번호 | 일자 | 품목 | 수량 | 합격 | 결과 | 검사자 │     │
│ │ INC-001 | 6/7 | 볼트 | 100 | 100 | PASS | 김검사 │     │
│ │ INC-002 | 6/7 | 너트 | 200 | 195 | PASS | 이검사 │     │
│ └─────────────────────────────────────────────────┘     │
│                                                          │
│ 📊 일별 검사 현황           📊 검사 유형별 합격률          │
│ ┌───────────────────┐     ┌───────────────────┐       │
│ │ [막대그래프]       │     │ [막대그래프]       │       │
│ │ 입고/공정/출하     │     │ 입고: 98.5%       │       │
│ │ 일별 추이         │     │ 공정: 97.2%       │       │
│ └───────────────────┘     └───────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 3. SPC (통계적 공정 관리) 화면
```
┌─────────────────────────────────────────────────────────┐
│ 📊 SPC - 통계적 공정 관리                                  │
├─────────────────────────────────────────────────────────┤
│ 공정: [가공공정 ▼] 품목: [ITEM001 ▼] 특성: [길이 ▼] 기간: [주 ▼] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📈 X-bar 관리도                📈 R 관리도              │
│ ┌───────────────────┐         ┌───────────────────┐    │
│ │     UCL: 10.5     │         │     UCL: 0.5      │    │
│ │ ----●--●--●------ │         │ ----●--●--●------ │    │
│ │     CL: 10.0      │         │     CL: 0.25      │    │
│ │ ----●--●--●------ │         │ ----●--●--●------ │    │
│ │     LCL: 9.5      │         │     LCL: 0         │    │
│ └───────────────────┘         └───────────────────┘    │
│                                                          │
│ 📊 공정 능력 분석              📊 정규성 검정            │
│ ┌───────────────────┐         ┌───────────────────┐    │
│ │ Cp : 1.33 ✅      │         │ [히스토그램]       │    │
│ │ Cpk: 1.25 ✅      │         │ [정규분포 곡선]    │    │
│ │ Pp : 1.28 ⚠️      │         │ P-value: 0.85     │    │
│ │ Ppk: 1.22 ⚠️      │         └───────────────────┘    │
│ └───────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

### 4. 불량 관리 화면
```
┌─────────────────────────────────────────────────────────┐
│ 🚫 불량 관리                                              │
├─────────────────────────────────────────────────────────┤
│ ┌────────┬────────┬────────┬────────┐                   │
│ │월간불량 │중대불량 │ 처리중  │  완료  │                   │
│ │  15건  │  2건   │  5건   │  8건   │                   │
│ └────────┴────────┴────────┴────────┘                   │
│                                                          │
│ 📊 불량 유형별 파레토 차트      [+ 불량 등록]              │
│ ┌─────────────────────────────────────────┐             │
│ │ 100% ─────────────────── 누적%          │             │
│ │  80% ─ ─ ─ ─ ─ ─ ─ ─ ─ 80% 기준선     │             │
│ │      █   █   █   █   █                  │             │
│ │      █   █   █   █   █                  │             │
│ │      치수 외관 기능 재료 포장             │             │
│ └─────────────────────────────────────────┘             │
│                                                          │
│ 📋 불량 이력                                              │
│ ┌─────────────────────────────────────────────────┐     │
│ │ 일자 | 유형 | 품목 | 수량 | 원인 | 조치 | 상태        │     │
│ │ 6/7 | 치수 | 볼트 | 2 | 공구마모 | 교체 | 완료       │     │
│ │ 6/6 | 외관 | 너트 | 1 | 스크래치 | 재작업 | 진행중    │     │
│ └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 5. 품질 성적서 화면
```
┌─────────────────────────────────────────────────────────┐
│ 📜 품질 성적서 관리                                        │
├─────────────────────────────────────────────────────────┤
│ 기간: [____~____] 고객: [전체 ▼] 제품: [전체 ▼] [🔍조회]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ [+ 성적서 발행] [📄 PDF 출력]                             │
│                                                          │
│ ┌─────────────────────────────────────────────────┐     │
│ │ 성적서번호 | 발행일 | 고객 | 제품 | LOT | 결과 | 발송  │     │
│ │ QC-0001  | 6/7  | A사 | 볼트 | L01 | 합격 | ✅      │     │
│ │ QC-0002  | 6/6  | B사 | 너트 | L02 | 합격 | ⏳      │     │
│ └─────────────────────────────────────────────────┘     │
│                                                          │
│ 📄 성적서 미리보기                                         │
│ ┌─────────────────────────────────────────┐             │
│ │          품 질 성 적 서                   │             │
│ │                                         │             │
│ │ 성적서번호: QC-20250607-0001            │             │
│ │ 고객사: (주)테크놀로지                   │             │
│ │                                         │             │
│ │ [검사 결과 테이블]                       │             │
│ │ 항목 | 규격 | 측정값 | 판정             │             │
│ │ 외관 | 양호 | 양호  | 합격             │             │
│ │ 치수 | 10±0.1 | 10.02 | 합격          │             │
│ │                                         │             │
│ │ 종합판정: 합 격                          │             │
│ └─────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 6. 품질 분석 대시보드
```
┌─────────────────────────────────────────────────────────┐
│ 📊 품질 분석                                              │
├─────────────────────────────────────────────────────────┤
│ 분석 기간: ○ 일별 ● 주별 ○ 월별 ○ 연간                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📈 품질 트렌드                 📊 품질 비용 분석           │
│ ┌───────────────────┐         ┌───────────────────┐    │
│ │ 합격률 ━━━━━      │         │   [파이 차트]      │    │
│ │ 98% ─ ─ ─ 목표   │         │ 예방: 45%         │    │
│ │ 불량률 ━━━━━      │         │ 평가: 30%         │    │
│ │ 시간 →            │         │ 실패: 25%         │    │
│ └───────────────────┘         └───────────────────┘    │
│                                                          │
│ 📊 공급업체별 품질             📋 품질 KPI                │
│ ┌───────────────────┐         ┌───────────────────┐    │
│ │ A사: 99.2% ████   │         │ 목표 불량률: 2.0%  │    │
│ │ B사: 98.5% ███    │         │ 실제 불량률: 1.8%  │    │
│ │ C사: 97.8% ██     │         │ 고객 클레임: 0건   │    │
│ │ ─ ─ ─ 98% 목표   │         │ Cpk: 1.33        │    │
│ └───────────────────┘         └───────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 7. 모바일 반응형 UI (V1.1 추가 개선)
```
📱 모바일 화면 (375px)
┌─────────────────┐
│ ☰ Smart MES-ERP │
├─────────────────┤
│ 📋 품질관리      │
├─────────────────┤
│ [검사] [불량]    │
│ [SPC] [성적서]   │
├─────────────────┤
│ 오늘 검사: 25건  │
│ 합격률: 98.5%   │
├─────────────────┤
│ 📊 검사 현황     │
│ ┌──────────┐    │
│ │ [그래프]  │    │
│ └──────────┘    │
├─────────────────┤
│ [+ 검사 등록]    │
└─────────────────┘
```

## 🎨 UI/UX 개선사항 (V1.1)

### 1. 색상 코드 표준화
- ✅ 합격/정상: #28a745 (녹색)
- ⚠️ 주의/경고: #ffc107 (노란색)
- ❌ 불합격/위험: #dc3545 (빨간색)
- ℹ️ 정보: #17a2b8 (청록색)

### 2. 아이콘 체계
- 🔍 검사: magnifying glass
- 📊 차트: bar chart
- ⚠️ 불량: warning triangle
- 🔧 장비: wrench
- 📜 성적서: scroll

### 3. 대시보드 위젯
- 실시간 업데이트 인디케이터
- 드래그 앤 드롭 대시보드 커스터마이징
- 전체화면 모드 지원

### 4. 접근성 개선
- 고대비 모드
- 키보드 네비게이션
- 스크린 리더 지원
- 툴팁 도움말

## 📐 레이아웃 그리드

### 데스크톱 (1200px+)
- 12 컬럼 그리드
- 사이드바: 2 컬럼
- 메인 콘텐츠: 10 컬럼
- 카드 간격: 16px

### 태블릿 (768px-1199px)
- 8 컬럼 그리드
- 사이드바 접힘
- 카드 2열 배치

### 모바일 (767px 이하)
- 4 컬럼 그리드
- 단일 컬럼 레이아웃
- 하단 네비게이션

## 🔄 인터랙션 플로우

### 검사 등록 프로세스
1. [+ 검사 등록] 클릭
2. 모달 팝업 표시
3. 검사 유형 선택 → 품목 선택 → 수량 입력
4. 자동 샘플 수 계산
5. 검사 결과 입력
6. 저장 → 실시간 대시보드 업데이트

### SPC 분석 플로우
1. 공정/품목/특성 선택
2. 데이터 자동 로드
3. 관리도 실시간 생성
4. 이상점 자동 감지 및 알림
5. 원인 분석 입력 프롬프트

## 🎯 V1.1 핵심 개선사항

1. **실시간 모니터링 강화**
   - WebSocket 기반 실시간 알림
   - 자동 새로고침 없이 데이터 업데이트

2. **모바일 최적화**
   - 터치 제스처 지원
   - 오프라인 모드 (일부 기능)

3. **데이터 시각화 개선**
   - 애니메이션 차트
   - 대화형 그래프
   - 3D 파레토 차트 옵션

4. **성능 최적화**
   - 레이지 로딩
   - 데이터 페이지네이션
   - 캐싱 전
