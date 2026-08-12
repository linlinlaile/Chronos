import com.alibaba.fastjson.JSON;
import com.common.HttpUtil;
import com.entity.Course;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpEntity;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PostTest {
    public static void main(String[] args) throws Exception {
        updateScore();
    }
    public static void update(String[] args) throws IOException {
        Map<String, Object> start_course_session_body = new HashMap<>();
        start_course_session_body.put("courseId", "70482");
        start_course_session_body.put("delay", 1200);
        start_course_session_body.put("logId", 1380122);
        start_course_session_body.put("sign", "CXv2Gk");
        String response = sendPost("https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/updateStudy", assertHeader(), JSON.toJSONString(start_course_session_body));
        System.out.println(response);
    }
    public static void start() throws IOException {
        Map<String, Object> start_course_session_body = new HashMap<>();
        start_course_session_body.put("courseId", "70482");
        start_course_session_body.put("delay", 1200);
        String response = sendPost("https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/startPlay", assertHeader(), JSON.toJSONString(start_course_session_body));
        System.out.println(response);
    }

    private static void pause() throws IOException {
        String response = sendPost("https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/autoPause",
                assertHeader(), JSON.toJSONString(new HashMap<>()));
        System.out.println(response);
    }

    private static void confirm() throws IOException {
        String response = sendPost("https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/confirmPlay",
                assertHeader(), JSON.toJSONString(new HashMap<>()));
        System.out.println(response);
    }

    private static void updateScore() throws Exception {
        String response = sendPost("https://learning.hzrs.hangzhou.gov.cn/api/index/Study.UserIndex/index",
                assertHeader(), JSON.toJSONString(new HashMap<>()));
        System.out.println(extractStudyScore(response));
    }

    private static String extractStudyScore(String response) throws Exception {
        // 假设这是你的JSON字符串
        String json = "{\"status\":200,\"data\":{\"course\":[{\"fsc_id\":\"65306095\",\"studentid\":\"448016\",\"courseid\":\"66529\",\"validstudytime\":\"2400.00\",\"coursename\":\"发挥平台企业引领作用，促进数字经济加快发展（下）\",\"credithour\":\"1.00\",\"period\":\"1.00\",\"examtype\":\"W\",\"url\":\"https://xc-course.hzrs.hangzhou.gov.cn:5443/zj/2024/zy24075/zj.html\",\"professional_field_id\":\"1,9\",\"coursetype_text\":\"专业课程\"},{\"fsc_id\":\"65289103\",\"studentid\":\"448016\",\"courseid\":\"67017\",\"validstudytime\":\"925.00\",\"coursename\":\"数据分析之SQL零基础到实战应用高阶课——CASE转置应用\",\"credithour\":\"0.50\",\"period\":\"0.50\",\"examtype\":\"W\",\"url\":\"https://xc-jnk.hzrs.hangzhou.gov.cn:7443/index.html?coursename=数据分析之SQL零基础到实战应用高阶课——CASE转置应用&courseUrl=/2024/hygx/CASE与IF函数 CASE转置应用&\",\"professional_field_id\":\"1\",\"coursetype_text\":\"行业公需\"},{\"fsc_id\":\"57509731\",\"studentid\":\"448016\",\"courseid\":\"66528\",\"validstudytime\":\"1920.00\",\"coursename\":\"发挥平台企业引领作用，促进数字经济加快发展（中）\",\"credithour\":\"1.00\",\"period\":\"1.00\",\"examtype\":\"W\",\"url\":\"https://xc-course.hzrs.hangzhou.gov.cn:5443/zj/2024/zy24074/zj.html\",\"professional_field_id\":\"1,9\",\"coursetype_text\":\"专业课程\"},{\"fsc_id\":\"57508870\",\"studentid\":\"448016\",\"courseid\":\"66527\",\"validstudytime\":\"1980.00\",\"coursename\":\"发挥平台企业引领作用，促进数字经济加快发展（上）\",\"credithour\":\"1.00\",\"period\":\"1.00\",\"examtype\":\"W\",\"url\":\"https://xc-course.hzrs.hangzhou.gov.cn:5443/zj/2024/zy24073/zj.html\",\"professional_field_id\":\"1,9\",\"coursetype_text\":\"专业课程\"},{\"fsc_id\":\"57451418\",\"studentid\":\"448016\",\"courseid\":\"70546\",\"validstudytime\":\"3060.00\",\"coursename\":\"植被参数遥感反演及应用：第3章 植被水分和生态干旱遥感\",\"credithour\":\"1.00\",\"period\":\"1.00\",\"examtype\":\"W\",\"url\":\"https://xc-course.hzrs.hangzhou.gov.cn:5443/zj/vod/index.html?coursename=植被参数遥感反演及应用：第3章 植被水分和生态干旱遥感&courseUrl=/2024/植被参数遥感反演及应用：第3章 植被水分和生态干旱遥感&\",\"professional_field_id\":\"8\",\"coursetype_text\":\"一般公需\"}],\"personal\":[],\"study\":[{\"tans\":0,\"coursetype\":\"一般公需\",\"r\":\"0.0\",\"s\":\"1.0\",\"w\":0,\"typeid\":\"17\",\"personal\":\"0.0\",\"yestoday\":\"0.0\"},{\"tans\":0,\"coursetype\":\"行业公需\",\"r\":\"0.0\",\"s\":\"0.0\",\"w\":\"0.0\",\"typeid\":\"16\",\"personal\":\"0.0\",\"yestoday\":\"0.0\"},{\"tans\":0,\"coursetype\":\"专业课程\",\"r\":\"60.0\",\"s\":\"1.0\",\"w\":\"59.0\",\"typeid\":\"15\",\"personal\":\"0.0\",\"yestoday\":\"0.0\"},{\"tans\":0,\"coursetype\":\"总学时\",\"r\":\"90.0\",\"s\":\"2.0\",\"w\":\"88.0\",\"typeid\":0,\"personal\":\"0.0\",\"yestoday\":\"0.0\"}]},\"app_use_time\":0.08601093292236328,\"total_used_time\":0.09067296981811523}";

        // 使用Jackson解析JSON
        ObjectMapper mapper = new ObjectMapper();
        Map<String, Object> root = mapper.readValue(json, Map.class);
        Map<String, Object> data = (Map<String, Object>) root.get("data");
        List<Map<String, Object>> study = (List<Map<String, Object>>) data.get("study");

        // 初始化分数变量
        String generalRequiredScore = "0";
        String industryRequiredScore = "0";
        String professionalCourseScore = "0";

        // 遍历study数组提取分数
        for (Map<String, Object> item : study) {
            String courseType = (String) item.get("coursetype");
            String score = item.get("s").toString();

            switch (courseType) {
                case "一般公需":
                    generalRequiredScore = score;
                    break;
                case "行业公需":
                    industryRequiredScore = score;
                    break;
                case "专业课程":
                    professionalCourseScore = score;
                    break;
            }
        }

        // 格式化输出
        return String.format("一般公需：%s分，行业公需：%s分，专业课程：%s分",
                generalRequiredScore, industryRequiredScore, professionalCourseScore);
    }

    private static Map<String, String> assertHeader() {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json, text/plain, */*");
        headers.put("Accept-Encoding", "gzip, deflate, br, zstd");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8,sw;q=0.7");
//        headers.put("Authorization", "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJrM2lzQCRkc281XiZBOEZIKkRGSSIsImF1ZCI6ImNsdyIsImlhdCI6MTczOTI1ODQ0NCwibmJmIjoxNzM5MjU4NDQ0LCJleHAiOjE3MzkyNjIwNDQsImRhdGEiOnsic3R1ZGVudGlkIjoiNDQ4MDE2In19.3h-o1fnaXZ3Oecnugq7o7LGW1mMJvClXQQOZgyTDYqk");
        headers.put("Connection", "keep-alive");
//        headers.put("Content-Length", "33");
        headers.put("Content-Type", "application/json");
        headers.put("Cookie", "__sid__=6111608557; __loginuser__=339005199111170334; Hm_lvt_de1beef062ce941f1ebcd905eab09f70=1722309361,1722486664,1722828045,1723807270; HZSRHANGZHOU=f947726919457fc8f36153ea800987d5; Stauthorization=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJrM2lzQCRkc281XiZBOEZIKkRGSSIsImF1ZCI6ImNsdyIsImlhdCI6MTc0NTgzMTI1OCwibmJmIjoxNzQ1ODMxMjU4LCJleHAiOjE3NDU4MzQ4NTgsImRhdGEiOnsic3R1ZGVudGlkIjoiNDQ4MDE2In19.AmdWh3vodjAS2rhndYCkixhzFHe_wx0lkEZJk9jo-0Y; BIGipServerxgx_web_pool=!iXySKQ68MWO2hbgBpN3lutBoukYbQ/EUiJ8K5fGQmOnXzG280imaOF4IQ11bIZMHoIvNbU2tCCGenw==");
        headers.put("Host", "learning.hzrs.hangzhou.gov.cn");
        headers.put("Origin", "https://learning.hzrs.hangzhou.gov.cn");
        headers.put("Referer", "https://learning.hzrs.hangzhou.gov.cn/");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36");
        return headers;
    }

    public static String sendPost(String url,
                                  Map<String, String> headers,
                                  String jsonBody) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost httpPost = new HttpPost(url);
            // 添加自定义 Header
            if (headers != null) {
                for (Map.Entry<String, String> entry : headers.entrySet()) {
                    httpPost.setHeader(entry.getKey(), entry.getValue());
                }
            }
            // 设置 JSON 请求体
            if (jsonBody != null) {
                httpPost.setEntity(new StringEntity(
                        jsonBody,
                        ContentType.APPLICATION_JSON
                ));
            }

            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                HttpEntity entity = response.getEntity();
                if (entity != null) {
                    return EntityUtils.toString(entity);
                } else {
                    throw new IOException("Empty response");
                }
            }
        }
    }
}
