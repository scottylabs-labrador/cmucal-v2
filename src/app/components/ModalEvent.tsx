import Modal from './Modal';
import { formatDate } from "~/utils/dateService";
import { EventType } from '../types/EventType';
import axios from "axios";
import { User } from 'lucide-react';
import { useUser } from "@clerk/nextjs";
import { useEffect, useState } from 'react';
import { userAgent } from 'next/server';

type ModalEventProps = {
    show: boolean;
    onClose: () => void;
    toggleAdded: (eventId:string) => void;
    eventId: string;
}

export default function ModalEvent({ show, onClose, toggleAdded, eventId }: ModalEventProps) {
    if (eventId=="") return null;
    const { user } = useUser();
    const [eventDetails, setEventDetails] = useState<EventType | null>(null);

    useEffect(() => {
        // get specific event with ID
        axios.get(`http://localhost:5001//api/events/${eventId}`, {
            params: {
                user_id: user?.id,
            },
            withCredentials: true,
        })
            .then(res => setEventDetails(res.data))
            .catch(err => console.error("Failed to fetch event:", eventId, err));
    }, [eventId])
    

    return (
        <Modal show={show} onClose={onClose}>
            <div>
                {eventDetails && (
                    <>
                <p className="text-lg">{eventDetails.title}</p>
                <p className="text-base text-gray-500">{formatDate(eventDetails.start_datetime)} - {formatDate(eventDetails.end_datetime)}</p>
                <p className="text-base text-gray-500">{eventDetails.location}</p>
                {eventDetails.org && (<p className="text-base text-gray-500">Hosted by {eventDetails.org}</p>)}
                <p className="text-base text-gray-500 py-4">{eventDetails.description || "No additional details available."}</p>
                <button 
                className={`mt-2 px-4 py-2 rounded-md w-full ${
                    eventDetails.user_saved ? "bg-blue-300" : "bg-blue-500"
                } text-white`}
                    onClick={() => {toggleAdded(eventDetails.id); onClose()}}>
                   { eventDetails.user_saved ? "Remove" : "Add" }
                </button> </>)}
            </div>
        </Modal>

    )
}
