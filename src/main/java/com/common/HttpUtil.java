package com.common; /**
 * Copyright (c) 2015-2016, Chill Zhuang 庄骞 (smallchill@163.com).
 * <p>
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * <p>
 * http://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import com.alibaba.fastjson.JSON;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpEntity;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.util.EntityUtils;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.util.*;

@Slf4j
public class HttpUtil {
    public static String getIp() {
        return HttpUtil.getRequest().getRemoteHost();
    }

    /**
     * 获取所有请求的值
     */
    public static Map<String, String> getRequestParameters() {
        HashMap<String, String> values = new HashMap<>();
        HttpServletRequest request = HttpUtil.getRequest();
        Enumeration enums = request.getParameterNames();
        while (enums.hasMoreElements()) {
            String paramName = (String) enums.nextElement();
            String paramValue = request.getParameter(paramName);
            values.put(paramName, paramValue);
        }
        return values;
    }

    public static HttpServletResponse getResponse() {
        HttpServletResponse response = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getResponse();
        return response;
    }

    public static HttpServletRequest getRequest() {
        HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
        return request;
    }

    /**
     * 向指定URL发送GET方法的请求
     *
     * @param url   发送请求的URL
     * @param param 请求参数
     * @return URL 所代表远程资源的响应结果
     */
    public static String sendGet(String url, Map<String, String> param) {
        String result = "";
        BufferedReader in = null;
        try {
            StringBuffer query = new StringBuffer();

            for (Map.Entry<String, String> kv : param.entrySet()) {
                query.append(URLEncoder.encode(kv.getKey(), "UTF-8") + "=");
                query.append(URLEncoder.encode(kv.getValue(), "UTF-8") + "&");
            }
            if (query.lastIndexOf("&") > 0) {
                query.deleteCharAt(query.length() - 1);
            }

            String urlNameString = url + "?" + query.toString();
            URL realUrl = new URL(urlNameString);
            // 打开和URL之间的连接
            URLConnection connection = realUrl.openConnection();
            // 设置通用的请求属性
            connection.setRequestProperty("accept", "*/*");
            connection.setRequestProperty("connection", "Keep-Alive");
            connection.setRequestProperty("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;SV1)");
            // 建立实际的连接
            connection.connect();
            // 获取所有响应头字段
            Map<String, List<String>> map = connection.getHeaderFields();
            // 遍历所有的响应头字段
            for (String key : map.keySet()) {
                System.out.println(key + "--->" + map.get(key));
            }
            // 定义 BufferedReader输入流来读取URL的响应
            in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String line;
            while ((line = in.readLine()) != null) {
                result += line;
            }
        } catch (Exception e) {
            System.out.println("发送GET请求出现异常！" + e);
            e.printStackTrace();
        }
        // 使用finally块来关闭输入流
        finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        return result;
    }

    /**
     * 向指定 URL 发送POST方法的请求
     *
     * @param url   发送请求的 URL
     * @param param 请求参数
     * @return 所代表远程资源的响应结果
     */
    public static String sendPost(String url, Map<String, String> param, Map<String, String> header) {
        HttpPost post = new HttpPost(url);
        try {
            System.out.println(JSON.toJSONString(param));
            //创建参数集合
            List<BasicNameValuePair> list = new ArrayList<>();
            //添加参数
            if (param != null) {
                for (String str : param.keySet()
                ) {
                    list.add(new BasicNameValuePair(str, param.get(str)));
                }
            }
            //把参数放入请求对象，，post发送的参数list，指定格式
            post.setEntity(new UrlEncodedFormEntity(list, "UTF8"));

            if (header != null) {
                for (String str : header.keySet()
                ) {
                    post.addHeader(str, header.get(str));
                }
            }
            CloseableHttpClient client = HttpClients.createDefault();
            //启动执行请求，并获得返回值
            CloseableHttpResponse response = client.execute(post);
            //得到返回的entity对象
            HttpEntity entity = response.getEntity();
            //把实体对象转换为string
            String result = EntityUtils.toString(entity, "UTF8");
            //为防止频繁调用一个接口导致接口爆掉，每次调用完成后停留100毫秒
            Thread.sleep(100);
            //返回内容
            System.out.println(result);
            return result;
        } catch (Exception e1) {
            e1.printStackTrace();
            return "";
        }
    }

}
