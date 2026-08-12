package com;

import com.alibaba.fastjson.JSON;
import com.common.FileUtil;
import com.stuty.StudyProcessor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.stereotype.Component;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

/**
 * @Auther: wll
 * @Date: 20-2-27 15:13
 * @Description:
 */
@SpringBootApplication
@EnableScheduling
public class Starter {
    public static void main(String[] args) {
        SpringApplication.run(Starter.class, args);
    }

    @Component
    class Runner implements CommandLineRunner {
        @Autowired
        private StudyProcessor processor;

        @Override
        public void run(String... args) throws Exception {
//            processor.main(args);
//            Map<String, Map<Integer, Integer>> index = new HashMap<>();
//            Map<Integer,Integer> m = new HashMap<>();
//            m.put(2,3);
//            index.put("aaa",m);
//            FileUtil.write(JSON.toJSONString(index),new File("data"));
//            String s = FileUtil.read(new File("data"));
//            Map<String, Map<Integer, Integer>> index2 = (Map<String, Map<Integer, Integer>>) JSON.parse(s);
//            System.out.println(index2);

        }
    }
}
