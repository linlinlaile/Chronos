package com.wang.webmagic;

import redis.clients.jedis.Jedis;
import us.codecraft.webmagic.ResultItems;
import us.codecraft.webmagic.Task;
import us.codecraft.webmagic.pipeline.Pipeline;

import java.io.File;
import java.util.List;
import java.util.Map;

/**
 * @Auther: wll
 * @Date: 19-5-10 13:41
 * @Description:
 */
public class KkpmhPipeline implements Pipeline {
    private Jedis jedis = new Jedis("106.15.226.131", 6379);
    private String picture_path = "/home/telek/crawpictures";

    @Override
    public void process(ResultItems resultItems, Task task) {
        String title = resultItems.get("title");
        String chapters = resultItems.get("chapters");
        List<PictureInfo> pictures = resultItems.get("pictures");
        System.out.println("完成" + chapters + "爬取,开始下载图片");
        File file = new File(picture_path + File.separator + title + File.separator + chapters + File.separator);
        if (file.exists()) {
            System.out.println("完成" + chapters + "图片下载");
            return;
        }
        for (PictureInfo picture : pictures) {
            //TODO 下载图片
            String filePath = picture_path + File.separator + title + File.separator + chapters + File.separator + picture.getPictureName();
            DownloadUtil.download(picture.getPictureUrl(), filePath);
        }
        System.out.println("完成" + chapters + "图片下载");
    }
}
