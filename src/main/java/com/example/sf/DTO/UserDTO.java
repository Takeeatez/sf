package com.example.sf.DTO;

import lombok.*;

import java.time.LocalDateTime;

@Data
@Builder
@ToString
@AllArgsConstructor
@NoArgsConstructor
public class UserDTO {
    private Long id;
    private String userId;
    private String userName;
    private String password;
    private String email;
    private String phone;
    private String profileImage;
    private String role;
    private LocalDateTime createdAt;  // 가입 날짜

}
