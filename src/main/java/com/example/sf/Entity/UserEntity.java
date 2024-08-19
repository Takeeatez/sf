package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.util.List;

@Entity
@Getter
@Setter
@ToString
@Builder
@AllArgsConstructor
@Table(name = "users") // 테이블 이름을 "users"로 지정
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(length = 12, unique = true, nullable = false)
    private String userId; // 사용자 아이디

    @Column(length = 8, nullable = false)
    private String userName;

    @Column(nullable = false)
    private String password; // 비밀번호

    @Column(nullable = false, length = 20)
    private String email; // 이메일

    @Column(nullable = false)
    private String phone; // 전화번호

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role; // 사용자 역할

    @Column(name = "consecutive_login_days", nullable = false)
    @Builder.Default
    private int consecutiveLoginDays = 0; // 연속 로그인 일수

    @Column(name = "last_login_date")
    private LocalDate lastLoginDate; // 마지막 로그인 날짜

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ExerciseRecordEntity> exerciseRecords; // 운동 기록 리스트

    // 사용자 역할 정의
    public enum Role {
        USER("USER", "회원"),
        ADMIN("ADMIN", "관리자");

        @Getter
        private final String key;
        @Getter
        private final String value;

        Role(String key, String value) {
            this.key = key;
            this.value = value;
        }
    }

    public void updateLoginStreak() {
        LocalDate today = LocalDate.now();
        if (this.lastLoginDate != null && this.lastLoginDate.equals(today.minusDays(1))) {
            this.consecutiveLoginDays += 1;
        } else if (this.lastLoginDate == null || !this.lastLoginDate.equals(today)) {
            this.consecutiveLoginDays = 1;
        }
        this.lastLoginDate = today;
    }

    public void addExerciseRecord(ExerciseRecordEntity record) {
        this.exerciseRecords.add(record);
        record.setUser(this);
    }
}
