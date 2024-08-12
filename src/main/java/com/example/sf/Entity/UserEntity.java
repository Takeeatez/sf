package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.*;

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

    @Column(nullable = false)
    private String password; // 비밀번호

    @Column(nullable = false, length = 20)
    private String email; // 이메일

    @Column(nullable = false)
    private String phone; // 전화번호

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role; // 사용자 역할

    // 사용자 역할 정의
    public enum Role {
        USER("USER", "회원"),
        ADMIN("ADMIN", "관리자");

        @Getter
        private final String key;
        @Getter
        private final String value;

        Role(String key, String value){
            this.key = key;
            this.value = value;
        }
    }

    //@OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    //private List<Fitness> fitnessRecords = new ArrayList<>();
}
