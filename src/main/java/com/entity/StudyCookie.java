package com.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
public class StudyCookie {
    private String name;
    private String value;
    private int type;
    private String state;
    private String score;

    public StudyCookie(String name, String value, int type) {
        this.name = name;
        this.value = value;
        this.type = type;
        this.state = "正常";
    }

    @Override
    public boolean equals(Object o1) {
        if (o1 == this)
            return true;
        if (o1 == null || o1.getClass() != getClass())
            return false;
        StudyCookie studyCookie = (StudyCookie) o1;
        return name != null && value != null && (name.equals(studyCookie.getName()) || value.equals(studyCookie.getValue()));
    }

    @Override
    public int hashCode() {
        return name.hashCode();
    }
}
