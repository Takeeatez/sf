package com.example.sf.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserChoiceDTO {

    private String choicePK;
    private Long userId; // UserEntity의 ID를 참조하는 필드
    private Integer fitnessTypeId; // FitnessTypeEntity의 ID를 참조하는 필드
    private String time;
    private String num;
    private String date;
    private String sets;
    private String rate;

    private String userName; // UserEntity의 userName을 담기 위한 필드
    private String fitnessTypeName; // FitnessTypeEntity의 name을 담기 위한 필드
}
