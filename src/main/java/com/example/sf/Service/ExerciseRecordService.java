package com.example.sf.Service;

import com.example.sf.Entity.ExerciseRecordEntity;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.ExerciseRecordRepository;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class ExerciseRecordService {

    private final ExerciseRecordRepository exerciseRecordRepository;
    private final UserRepository userRepository;

    @Transactional
    public void saveExerciseType(String exerciseType, String userId) {
        UserEntity user = userRepository.findByUserId(userId)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        ExerciseRecordEntity exerciseRecord = ExerciseRecordEntity.builder()
                .user(user)
                .exerciseType(exerciseType)
                .build();

        exerciseRecordRepository.save(exerciseRecord);
    }

    public void saveRepsAndSets(int reps, int sets, String userId) {
        // userId를 기반으로 UserEntity 객체를 조회합니다.
        UserEntity user = userRepository.findByUserId(userId)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        // 가장 최근에 생성된 레코드를 찾음
        ExerciseRecordEntity latestRecord = exerciseRecordRepository.findTopByUserOrderByIdDesc(user)
                .orElseThrow(() -> new IllegalStateException("No exercise record found"));

        // reps와 sets 업데이트
        latestRecord.setReps(reps);
        latestRecord.setSets(sets);

        // 업데이트된 레코드 저장
        exerciseRecordRepository.save(latestRecord);
    }

    @Transactional
    public void saveExerciseDetails(LocalDate exerciseDate, String exerciseTime, double achievementRate,
            String userId) {
        // userId를 기반으로 UserEntity 객체를 조회합니다.
        UserEntity user = userRepository.findByUserId(userId)
                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

        // 가장 최근에 생성된 레코드를 찾음
        ExerciseRecordEntity latestRecord = exerciseRecordRepository.findTopByUserOrderByIdDesc(user)
                .orElseThrow(() -> new IllegalStateException("No exercise record found"));

        // exerciseDate, exerciseTime, achievementRate 업데이트
        latestRecord.setExerciseDate(exerciseDate);
        latestRecord.setExerciseTime(exerciseTime);
        latestRecord.setAchievementRate(achievementRate);

        // 업데이트된 레코드 저장
        exerciseRecordRepository.save(latestRecord);
    }

}