package com.example.sf.Service;

import com.example.sf.DTO.UserChoiceDTO;
import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Entity.UserChoiceEntity;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.FitnessTypeRepository;
import com.example.sf.Repository.UserChoiceRepository;
import com.example.sf.Repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@RequiredArgsConstructor
public class UserChoiceService {

    private final UserChoiceRepository userChoiceRepository;
    private final UserRepository userRepository;
    private final FitnessTypeRepository fitnessTypeRepository;

    @Transactional
    public void saveUserChoice(UserChoiceDTO userChoiceDTO) {
        // User 찾기
        UserEntity user = userRepository.findByUserName(userChoiceDTO.getUserName())
                .orElseThrow(() -> new RuntimeException("User not found with username: " + userChoiceDTO.getUserName()));

        // FitnessType 찾기
        FitnessTypeEntity fitnessType = fitnessTypeRepository.findByFitId(userChoiceDTO.getFitnessTypeId())
                .orElseThrow(() -> new RuntimeException("FitnessType not found with ID: " + userChoiceDTO.getFitnessTypeId()));

        // UserChoiceEntity 생성
        UserChoiceEntity userChoiceEntity = new UserChoiceEntity();
        userChoiceEntity.setChoicePK(userChoiceDTO.getChoicePK());
        userChoiceEntity.setUser(user);
        userChoiceEntity.setFitnessType(fitnessType);
        userChoiceEntity.setNum(userChoiceDTO.getNum());
        userChoiceEntity.setSets(userChoiceDTO.getSets());
        userChoiceEntity.setRate(userChoiceDTO.getRate());
        userChoiceEntity.setDate(LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        userChoiceEntity.setTime(userChoiceDTO.getTime());

        // 저장
        userChoiceRepository.save(userChoiceEntity);
    }
}