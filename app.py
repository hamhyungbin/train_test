from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# ODsay API 키
ODSAY_API_KEY = '0nirxycz5C6uGM1oCdW6JQ' 

# 수도권 지하철 노선 정보 (간단한 색상 매핑용)
SUBWAY_LINE_COLORS = {
    '1': '#0052A4', '2': '#00A84D', '3': '#EF7C1C', '4': '#00A4E3',
    '5': '#996CAC', '6': '#CD7C2F', '7': '#747F00', '8': '#E6186C', '9': '#BDB092',
    '경의중앙선': '#77C4A3', '공항철도': '#0090D2', '수인분당선': '#F5A200', '신분당선': '#D4003B'
}

@app.route('/')
def index():
    # 첫 화면: 검색 폼을 보여줌
    return render_template('index.html')

@app.route('/search_route')
def search_route():
    start_station = request.args.get('start_station')
    end_station = request.args.get('end_station')

    if not start_station or not end_station:
        return "출발역과 도착역을 모두 입력해주세요."

    # ODsay 대중교통 길찾기 API URL
    search_url = f"https://api.odsay.com/v1/api/subwayPath?lang=0&CID=1000&SID={start_station}&EID={end_station}&apiKey={ODSAY_API_KEY}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()  # 오류가 발생하면 예외를 발생시킴
        
        data = response.json()

        if "error" in data:
            # API에서 에러를 반환한 경우 (리스트의 첫번째 항목을 사용)
            error_message = data["error"][0]["message"] 
            return f"API 오류: {error_message}"

        # 결과 데이터를 가공하여 템플릿에 전달
        result_data = data.get('result', {})
        
        # 경로의 각 구간에 색상 정보 추가
        if 'driveInfoSet' in result_data and 'driveInfo' in result_data['driveInfoSet']:
            for leg in result_data['driveInfoSet']['driveInfo']:
                line_name = leg.get('laneName')
                # 간단한 이름 처리 (예: "수도권 1호선" -> "1")
                simple_name = line_name.split()[-1].replace('호선', '') if line_name else ''
                leg['lineColor'] = SUBWAY_LINE_COLORS.get(simple_name, '#333333') # 기본색상

        return render_template('result.html',
                               start=start_station,
                               end=end_station,
                               path_data=result_data)

    except requests.exceptions.RequestException as e:
        return f"HTTP 요청 오류: {e}"
    except json.JSONDecodeError:
        return "API 응답을 파싱하는 데 실패했습니다. 응답이 올바른 JSON 형식이 아닐 수 있습니다."

if __name__ == '__main__':
    app.run(debug=True)