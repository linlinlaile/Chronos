package com.common;

import org.apache.commons.lang3.StringUtils;

import java.io.*;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class FileUtil {
    public static void write(Map<String, Map<Integer, Integer>> map, File file) {
        FileWriter fileWriter = null;
        try {
            fileWriter = new FileWriter(file);
            for (Map.Entry entry : map.entrySet()) {
                String name = entry.getKey().toString();
                Map<Integer, Integer> m = (Map<Integer, Integer>) entry.getValue();
                for (Map.Entry entry1 : m.entrySet()) {
                    fileWriter.write(name + ":" + entry1.getKey() + "-" + entry1.getValue() + "\n");
                }
            }
            fileWriter.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void write(String str, File file) {
        FileWriter fileWriter = null;
        try {
            fileWriter = new FileWriter(file, true);
            fileWriter.write(str+"\r\n");
            fileWriter.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Map<String, Map<Integer, Integer>> read(File file) {
        Map<String, Map<Integer, Integer>> map = new HashMap<>();
        try {
            FileReader fileReader = new FileReader(file);
            BufferedReader buffReader = new BufferedReader(fileReader);
            while (buffReader.ready()) {
                String s = buffReader.readLine();
                if (StringUtils.isEmpty(s)) {
                    continue;
                }
                String name = s.split(":")[0];
                Integer type = Integer.parseInt(s.split(":")[1].split("-")[0]);
                Integer num = Integer.parseInt(s.split(":")[1].split("-")[1]);
                if (!map.containsKey(name)) {
                    Map<Integer, Integer> m = new HashMap<>();
                    m.put(type, num);
                    map.put(name, m);
                } else if (!map.get(name).containsKey(type)) {
                    map.get(name).put(type, num);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return map;
    }
}
