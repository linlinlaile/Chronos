package com.wang.webmagic;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;

/**
 * @Auther: wll
 * @Date: 19-5-10 15:18
 * @Description:
 */
public class DownloadUtil {
    public static void download(String urlStr, String filePath) {
        try {
            File file = new File(filePath);
            if (!file.exists()) {
                file.getParentFile().mkdirs();
                file.createNewFile();
            }
            URL url = new URL(urlStr);
            URLConnection con = null;
            con = url.openConnection();
            con.addRequestProperty("User-Agent", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)");
            InputStream inputStream = con.getInputStream();
            ByteArrayOutputStream outStream = new ByteArrayOutputStream();
            byte[] buf = new byte[1024];
            int len = 0;
            while ((len = inputStream.read(buf)) != -1) {
                outStream.write(buf, 0, len);
            }
            inputStream.close();
            outStream.close();
            FileOutputStream op = new FileOutputStream(file);
            op.write(outStream.toByteArray());
            op.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
