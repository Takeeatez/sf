package com.example.sf.DTO;

import lombok.Getter;
import lombok.Setter;
import java.time.LocalDate;

@Getter
@Setter
public class ExerciseRecordDTO {
    private String exerciseType; // 운동 종목
    private int reps; // 횟수
    private int sets; // 세트 수
    private LocalDate exerciseDate; // 운동 날짜
    private String exerciseTime; // 운동 시간
    private double achievementRate; // 달성률
}
