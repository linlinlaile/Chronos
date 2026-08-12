package com.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class Course {
    private int type;
    private String cookie;
    private String courseId;
    private String logId;
    private String sign;
}
