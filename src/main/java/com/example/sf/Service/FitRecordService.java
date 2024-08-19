package com.example.sf.Service;

import com.example.sf.Entity.FitRecordEntity;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.FitRecordRepository;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class FitRecordService {

        private final FitRecordRepository fitRecordRepository;
        private final UserRepository userRepository;

        @Transactional
        public void saveFitType(String fitType, String userId) {
                UserEntity user = userRepository.findByUserId(userId)
                                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

                FitRecordEntity fitRecord = FitRecordEntity.builder()
                                .user(user)
                                .fitType(fitType)
                                .build();

                fitRecordRepository.save(fitRecord);
        }

        public void saveCountsAndSets(int counts, int sets, String userId) {
                // userId를 기반으로 UserEntity 객체를 조회합니다.
                UserEntity user = userRepository.findByUserId(userId)
                                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

                // 가장 최근에 생성된 레코드를 찾음
                FitRecordEntity latestRecord = fitRecordRepository.findTopByUserOrderByIdDesc(user)
                                .orElseThrow(() -> new IllegalStateException("No fit record found"));

                // counts와 sets 업데이트
                latestRecord.setCounts(counts);
                latestRecord.setSets(sets);

                // 업데이트된 레코드 저장
                fitRecordRepository.save(latestRecord);
        }

        @Transactional
        public void saveFitDetails(LocalDate fitDate, String fitTime, double rate,
                        String userId) {
                // userId를 기반으로 UserEntity 객체를 조회합니다.
                UserEntity user = userRepository.findByUserId(userId)
                                .orElseThrow(() -> new UsernameNotFoundException("User not found"));

                // 가장 최근에 생성된 레코드를 찾음
                FitRecordEntity latestRecord = fitRecordRepository.findTopByUserOrderByIdDesc(user)
                                .orElseThrow(() -> new IllegalStateException("No fit record found"));

                // fitDate, fitTime, rate 업데이트
                latestRecord.setFitDate(fitDate);
                latestRecord.setFitTime(fitTime);
                latestRecord.setRate(rate);

                // 업데이트된 레코드 저장
                fitRecordRepository.save(latestRecord);
        }

}