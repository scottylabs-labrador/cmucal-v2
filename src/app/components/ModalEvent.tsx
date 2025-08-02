"use client";

import Modal from './Modal';
import { formatEventDate } from "~/app/utils/dateService";
import { EventType } from '../types/EventType';
import axios from "axios";
import { useUser } from "@clerk/nextjs";
import { useEffect, useState } from 'react';

type ModalEventProps = {
    show: boolean;
    onClose: () => void;
    toggleAdded: (eventId:string) => void;
    eventId: string;
}

export default function ModalEvent({ show, onClose, toggleAdded, eventId }: ModalEventProps) {
    if (eventId === "") return null;
    const { user } = useUser();
    const [eventDetails, setEventDetails] = useState<EventType | null>(null);

    useEffect(() => {
        if (!eventId || !user?.id) return;

        // First try to get the event occurrence details
        axios.get(`http://localhost:5001/api/events/user_saved_event_occurrences`, {
            params: {
                user_id: user?.id,
            },
            withCredentials: true,
        })
        .then(res => {
            // Find the specific occurrence
            const occurrence = res.data.find((e: any) => e.id === eventId);
            if (occurrence) {
                // If found, get the parent event details
                return axios.get(`http://localhost:5001/api/events/${occurrence.event_id}`, {
                    params: {
                        user_id: user?.id,
                    },
                    withCredentials: true,
                });
            }
            // If not found in occurrences, try getting it as a regular event
            return axios.get(`http://localhost:5001/api/events/${eventId}`, {
                params: {
                    user_id: user?.id,
                },
                withCredentials: true,
            });
        })
        .then(res => setEventDetails(res.data))
        .catch(err => {
            console.error("Failed to fetch event:", eventId, err);
            // If all fails, try getting it as a regular event
            axios.get(`http://localhost:5001/api/events/${eventId}`, {
                params: {
                    user_id: user?.id,
                },
                withCredentials: true,
            })
            .then(res => setEventDetails(res.data))
            .catch(err => console.error("Failed to fetch event as regular event:", eventId, err));
        });
    }, [eventId, user?.id]);
    
    const isAdmin = eventDetails?.user_is_admin;

    return (
        <Modal show={show} onClose={onClose}>
            <div>
                {eventDetails && (
                    <>
                        <p className="text-lg">{eventDetails.title}</p>
                        <p className="text-base text-gray-500">
                            {formatEventDate(eventDetails.start_datetime)} - {formatEventDate(eventDetails.end_datetime)}
                        </p>
                        <p className="text-base text-gray-500">{eventDetails.location}</p>
                        {eventDetails.org && (
                            <p className="text-base text-gray-500">Hosted by {eventDetails.org}</p>
                        )}
                        <p className="text-base text-gray-500 py-4">
                            {eventDetails.description || "No additional details available."}
                        </p>
                        <div className="flex gap-4">
                            <button 
                                className={`px-4 py-2 rounded-md ${isAdmin ? "flex-1" : "w-full"} ${
                                    eventDetails.user_saved ? "bg-blue-300" : "bg-blue-500"
                                } text-white`}
                                onClick={() => {toggleAdded(eventDetails.id); onClose()}}>
                                {eventDetails.user_saved ? "Remove" : "Add"}
                            </button> 
                            {isAdmin && (
                                <button 
                                    className="px-4 py-2 rounded-md flex-1 bg-gray-200"
                                    onClick={() => console.log("clicked edit...")}>
                                    Edit Event
                                </button>
                            )}
                        </div>
                    </>
                )}
            </div>
        </Modal>
    );
}
