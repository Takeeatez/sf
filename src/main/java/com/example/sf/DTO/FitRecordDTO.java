package com.example.sf.DTO;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDate;

@Getter
@Setter
public class FitRecordDTO {
    private String fitType; // 운동 종목
    private int counts; // 횟수
    private int sets; // 세트 수
    private LocalDate fitDate; // 운동 날짜
    private String fitTime; // 운동 시간
    private double rate; // 달성률
}
