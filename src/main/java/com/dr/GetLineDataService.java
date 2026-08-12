package com.dr;

import com.alibaba.fastjson.JSON;
import com.common.FileUtil;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
public class GetLineDataService {

    public static String[] userIds = {"3301316031700", "3309933805472", "3301321247168", "3306320063120", "3304140158329", "3301711050361", "3304520096900", "3306120546924", "3303720215711", "3301250072898", "3303520068910", "3301701023150", "3301270164419", "3306031000384", "3303290148512", "3306010971099", "3306022010870", "3306010085722", "3308570088591"};
    public static int start = 0;
    public static int end = 24;

    public static void main(String[] args) throws IOException, InterruptedException {
        fuhe96();
    }

    private static void fuhe96() throws IOException, InterruptedException {
        for (String userId : userIds) {
            Map<String, Object> jsonbody = new HashMap<>();
            jsonbody.put("ROOTFUNC", "queryUserMonitorLoad");
            jsonbody.put("consNo", userId);
            jsonbody.put("loadTime", "2025-08-11");
            jsonbody.put("lineType", "01");
            jsonbody.put("token", "0427632DB40D566E9C8E3C0E5EF0ACDF629275E4F41FFC77FE47C3E7FE8BD021AA2E658A52EDDDD097448152868EBBFDD63D7CF9889B391C92CB3E51E9B4B3B6D412FC4A7E102342AF8C70CE38C238290F2020D420F7D041B0155A79D1C27A350345263A4171C9719BEC14FCF663579D75C0E177520B8980A157BDBEDF6F61303C91991C23707511DC55C7B5CC3EB455CC6ED82DDAA5D265AA946E4148B283174BEE33B97A3E387E");
            String response = sendPost("https://zjvpp.zj.sgcc.com.cn/loadAggre/effective/userMonitor/load",
                    "INGRESSCOOKIE=51eb4876a3c71227", JSON.toJSONString(jsonbody));
            Map<String, List<Map<String, Object>>> map = (Map<String, List<Map<String, Object>>>) JSON.parse(response);
            List<Map<String, Object>> list = map.get("dataList");
            for (Map<String, Object> stringObjectMap : list) {
                //current，base_PEAK_BASE
                if (stringObjectMap.get("prop").toString().equals("base_PEAK_BASE")) {
                    List<String> datas = (List<String>) stringObjectMap.get("data");
                    String dat = StringUtils.join(datas, ";");
                    FileUtil.write(dat,new File("data2"));
                }
            }
        }
    }

    private static void jiesuan() throws IOException, InterruptedException {
        for (String userId : userIds) {
            Map<String, Object> jsonbody = new HashMap<>();
            jsonbody.put("ROOTFUNC", "queryUserMonitorLoad");
            jsonbody.put("consNo", userId);
            jsonbody.put("loadTime", "2025-08-11");
            jsonbody.put("lineType", "01");
            jsonbody.put("token", "0427632DB40D566E9C8E3C0E5EF0ACDF629275E4F41FFC77FE47C3E7FE8BD021AA2E658A52EDDDD097448152868EBBFDD63D7CF9889B391C92CB3E51E9B4B3B6D412FC4A7E102342AF8C70CE38C238290F2020D420F7D041B0155A79D1C27A350345263A4171C9719BEC14FCF663579D75C0E177520B8980A157BDBEDF6F61303C91991C23707511DC55C7B5CC3EB455CC6ED82DDAA5D265AA946E4148B283174BEE33B97A3E387E");
            String response = sendPost("https://zjvpp.zj.sgcc.com.cn/loadAggre/effective/userMonitor/load",
                    "INGRESSCOOKIE=51eb4876a3c71227", JSON.toJSONString(jsonbody));
            Map<String, List<Map<String, Object>>> map = (Map<String, List<Map<String, Object>>>) JSON.parse(response);
            List<Map<String, Object>> list = map.get("dataList");
            for (Map<String, Object> stringObjectMap : list) {
                //current，base_PEAK_BASE
                if (stringObjectMap.get("prop").toString().equals("base_PEAK_BASE")) {
                    List<String> datas = (List<String>) stringObjectMap.get("data");
                    String dat = StringUtils.join(datas, ",");
                    String res = calculateIntervalAverages(dat, start, end);
                    FileUtil.write(res,new File("data2"));
                }
            }
        }
    }

    public static String calculateIntervalAverages(String loadData, int startHour, int endHour) {
        // 将负荷数据字符串分割成数组
        String[] loadPoints = loadData.split(",");
        if (loadPoints.length != 96) {
            throw new IllegalArgumentException("负荷数据必须包含96个点");
        }

        // 计算开始和结束的索引
        int startIndex = startHour * 4; // 每小时4个点
        int endIndex = endHour * 4;

        if (startIndex < 0 || endIndex > 96 || startIndex >= endIndex) {
            throw new IllegalArgumentException("无效的时间范围");
        }

        List<String> results = new ArrayList<>();

        // 每30分钟计算一次平均值（3个点）
        for (int i = startIndex; i < endIndex; i += 2) {
            // 确保有3个点可以计算（最后一个区间可能不足3个点）
            if (i + 2 >= loadPoints.length) break;

            // 获取3个点的值
            double point1 = Double.parseDouble(loadPoints[i]);
            double point2 = Double.parseDouble(loadPoints[i + 1]);
            double point3 = Double.parseDouble(loadPoints[i + 2]);

            // 计算平均值
            double average = (point1 + point2 + point3) / 3;

            results.add(String.valueOf(Math.round(average)));
        }
        return String.join("；", results);
    }

    public static String sendPost(String url, String cookie, String jsonBody) throws IOException {
        Map<String, String> headers = new HashMap<>();
        headers.put("accept", "application/json, text/plain, */*");
        headers.put("accept-encoding", "gzip, deflate, br, zstd");
        headers.put("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6");
        headers.put("connection", "keep-alive");
        headers.put("content-type", "application/json");
        headers.put("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0");
        headers.put("cookie", cookie);
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost httpPost = new HttpPost(url);
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
                String res = "";
                if (entity != null) {
                    res = EntityUtils.toString(entity);
                }
                return res;
            }
        }
    }
}
