package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

@Entity
@Getter
@Setter
@ToString
@Builder
@AllArgsConstructor
@Table(name = "exercise_record")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class ExerciseRecordEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", referencedColumnName = "userId")
    private UserEntity user;

    private String exerciseType;// 운동 종목
    private int reps; // 횟수
    private int sets; // 세트 수
    private LocalDate exerciseDate; // 운동 날짜
    private String exerciseTime; // 운동 시간
    private double achievementRate; // 달성률
}
