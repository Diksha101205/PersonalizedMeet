package com.example.personalizedmeetbackend.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.personalizedmeetbackend.model.Meeting;

public interface MeetingRepository extends JpaRepository<Meeting, Long> {

    boolean existsByMeetingCode(String meetingCode);
}
