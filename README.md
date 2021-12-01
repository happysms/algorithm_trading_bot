# algorithm_trading_bot
분산 투자 시스템 트레이딩 봇

## **설명** 
- 용도: 시스템 트레이딩 봇

- 거래소: Bybit

- 기초자산: Bybit 선물 거래소에 상장된 암호화폐 선물 10종목 동일 비율로 분산, 적절히 백테스팅하여 파라미터 및 레버리지 설정

- 전략: (래리 윌리엄스의) 변동성 돌파 전략 + 이동평균 조건 설정 + 인버스 숏 셀링

- 레버리지: x2

## **사용한 기술 스택 및 서비스**
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144241845-f5acacca-9a8c-43fa-adce-3bb2a859461f.png" class="center" width="600" height="300" /></p>

## **시스템 구성도**
![image](https://user-images.githubusercontent.com/70648382/144239812-e06f5a9f-28b4-47d0-bd2f-3147bead5dbe.png)


## 기울인 노력
### **성능** 
- 배경: 여러 종목을 동시에 주문하는 상황에 Blocking이 걸려 정확한 매수 혹은 매도 포인트에서 거래를 하지 못하여 손실이 발생하였다.
- 해결: 시세 모니터링과 주문과 관련된 함수를 비동기 방식으로 바꾸어 Blocking 없이 거래가 실행되도록 하였다.

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144235297-4e27a026-5bde-4c3b-b3d9-f6766388e13b.png" class="center" width="500" height="350" /></p>

------------------
- 배경: 갑작스럽게 많은 종목을 한번에 주문을 하게될 경우 시스템에 부하가 생겨 원활하게 주문이 이루어지지 않을 수 있다고 판단하였다.
- 해결: 주문을 EC2에서 진행하지 않고, AWS Lambda를 사용하여 여러 주문을 각각 다른 컴퓨팅 환경에서 실행되도록 분산시켰다.
  - 이점 +a: 기능을 수행하는 부분을 분리시킴으로써 유지보수성을 높였다.
  - 이점 +a: AWS Lambda와 연결된 CloudWatch logs를 통해 실행 내역 및 에러 사항을 로그로 남길 수 있다는 장점이 있다.
 
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144236658-6aeb106e-16d7-4708-bb50-5939925de683.png" class="center" width="400" height="300" /></p>

----------------------------------

### **보안**
- 거래소의 API를 특정 IP환경에서만 호출할 수 있도록 설정하였다. (거래소 웹에서 별도 등록)

- 주문을 수행할 AWS Lambda 컴퓨팅 환경에 AWS VPC를 연결함으로써 고정 IP 환경을 구성하였다. (고정된 IP를 거래소 API에 적용)

- AWS Lambda 함수를 특정 IP환경에서만 호출할 수 있도록 설정한다. 여기서 특정 IP는 모니터링을 수행하는 EC2의 IP이다. 즉 나의 EC2 환경에서만 Call할 수 있도록 커스터마이징한 것이다.   
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144237330-0d351354-1654-4604-b967-b926a92ef6ba.png" class="center" width="600" height="300" /></p>

- 민감한 정보(AWS access key, 거래소 Api key 등)을 Amazon S3에 저장하고, 필요할 때마다 S3에 접근하여 읽도록 구현했다.

-------------------------------

### 편의

- 일일 봇 수익률 기록 자동화: 매일 9시 정각에 실행되도록 이벤트를 트리거링하여 MDD(최대 손실 낙폭), 일일수익률, 누적수익률을 데이터베이스(RDS)에 기록한다.
<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144238996-4b72dfe3-b3ed-4917-82c4-11b68fdf1a9a.png" class="center" width="600" height="150" /></p>

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144240165-582c66db-2978-4c9c-af3c-e493ae03acbe.png" class="center" width="600" height="100" /></p>

- 주문을 요청할 때 마다 Slack 메신저 봇을 통해 내역을 전송한다. (향후 좀 더 이쁘게 커스터마이징할 계획)

<p align="center"><img src="https://user-images.githubusercontent.com/70648382/144239522-8c407741-49d0-4920-ac63-b89430772030.png" class="center" width="600" height="150" /></p>


------------------------------------
## **향후 업데이트 및 기능 추가 계획**
- 다중 이용 투자 플랫폼으로 개선하여 인증된 다수의 사용자가 서비스를 이용할 수 있도록 할 예정 => AWS Cognito로 사용자 인증 서비스 구현 

- 거래내역 실시간 확인 Web 페이지 개발 => react.js로 web front 구현

- 거래 종목, 알고리즘 파라미터를 수정할 수 있는 GUI 개발(현재는 직접 json 파일을 수정하고 S3에 업로드하는 방식) => Nosql 사용, react.js로 web front 구현





