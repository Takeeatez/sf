package com.example.sf.DTO;

import lombok.*;
import org.springframework.format.annotation.DateTimeFormat;

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

    @DateTimeFormat(pattern = "yyyy-MM-dd")
    private LocalDateTime joinDate;  // 가입 날짜

}
