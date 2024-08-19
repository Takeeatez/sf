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
@Table(name = "fit_record")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class FitRecordEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", referencedColumnName = "userId")
    private UserEntity user;

    private String fitType;// 운동 종목
    private int counts; // 횟수
    private int sets; // 세트 수
    private LocalDate fitDate; // 운동 날짜
    private String fitTime; // 운동 시간
    private double rate; // 달성률
}
