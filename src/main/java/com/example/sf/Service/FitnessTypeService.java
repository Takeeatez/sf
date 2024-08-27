package com.example.sf.Service;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Repository.FitnessTypeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Transactional
public class FitnessTypeService {

    private final FitnessTypeRepository fitnessTypeRepository;


    // 운동 저장
    public FitnessTypeEntity saveExercise(FitnessTypeEntity fitnessTypeEntity) {
        return fitnessTypeRepository.save(fitnessTypeEntity);
    }

    // 운동 업데이트
    public FitnessTypeEntity updateExercise(FitnessTypeEntity fitnessTypeEntity) {
        Optional<FitnessTypeEntity> existingEntity = fitnessTypeRepository.findByFitId(fitnessTypeEntity.getFitId());
        if (existingEntity.isPresent()) {
            FitnessTypeEntity updatedEntity = existingEntity.get();
            updatedEntity.setName(fitnessTypeEntity.getName());
            updatedEntity.setDescription(fitnessTypeEntity.getDescription());
            return fitnessTypeRepository.save(updatedEntity);
        }
        return null;
    }

    // 운동 삭제
    public boolean deleteExercise(int fitId) {
        Optional<FitnessTypeEntity> existingEntity = fitnessTypeRepository.findById(fitId);
        if (existingEntity.isPresent()) {
            fitnessTypeRepository.delete(existingEntity.get());
            return true;
        }
        return false;
    }

    // 전체 운동 리스트 불러옴
    public List<FitnessTypeEntity> getAllFitnessTypes() {
        return fitnessTypeRepository.findAll();
    }

    public FitnessTypeEntity getExerciseById(int fitId) {
        return fitnessTypeRepository.findById(fitId).orElse(null);
    }

    // 운동 이름으로 찾기
    public FitnessTypeEntity getExerciseByName(String name) {
        return fitnessTypeRepository.findByName(name).orElse(null);
    }

}