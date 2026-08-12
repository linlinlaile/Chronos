package com.common;

import java.util.concurrent.*;
import java.util.HashMap;
import java.util.Map;

public class DynamicTaskManager {
    private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
    private static final Map<String, ScheduledFuture<?>> taskMap = new HashMap<>();
    public static void scheduleTask(String taskId, Runnable task) {
        // 提交任务，延迟20分钟执行（TimeUnit.MINUTES可替换为其他单位）
        ScheduledFuture<?> future = scheduler.schedule(task, 20, TimeUnit.MINUTES);
        taskMap.put(taskId, future);
    }

    public static boolean cancelTask(String taskId) {
        ScheduledFuture<?> future = taskMap.get(taskId);
        if (future != null) {
            // 参数true表示尝试中断正在执行的任务（若任务已开始）
            boolean cancelled = future.cancel(true);
            taskMap.remove(taskId);
            return cancelled;
        }
        return false;
    }
    // 其他业务逻辑代码...
}