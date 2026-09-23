package com.example.personalizedmeetbackend.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.personalizedmeetbackend.model.MeetingRecording;

public interface MeetingRecordingRepository extends JpaRepository<MeetingRecording, Long> {

    List<MeetingRecording> findByMeetingId(Long meetingId);
}
