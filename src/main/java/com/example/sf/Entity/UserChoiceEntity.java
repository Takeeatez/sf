package com.example.sf.Entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "choice")
public class UserChoiceEntity {

    @Id
    @Column(length = 255)
    private String choicePK;

    @ManyToOne
    @JoinColumn(name = "id", nullable = false)
    private UserEntity user;

    @ManyToOne
    @JoinColumn(name = "fitId", nullable = false)
    private FitnessTypeEntity fitnessType;

    @Column(length = 255)
    private String time;

    @Column(length = 255)
    private String num;

    @Column(length = 255)
    private String date;

    @Column(length = 255)
    private String sets;

    @Column(length = 255)
    private String rate;
}
