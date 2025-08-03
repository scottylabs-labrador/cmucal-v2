
import Modal from './Modal';
import ModalEventForm from './ModalEventForm'
import { useEventState } from "../../context/EventStateContext";

type ModalEventProps = {
    show: boolean;
    onClose: () => void;
    eventId?: string;
}

export default function ModalEventUpdate({ show, onClose, eventId }: ModalEventProps) {
    const { modalView, closeModal} = useEventState();
    console.log("show update modal!!", show)

    return (
        // <ModalEventForm
        // show={show}
        // onClose={onClose}></ModalEventForm>
        <Modal show={show} onClose={onClose}>
            heyyyy
        </Modal>
    )
    
}