import { useState, useEffect } from "react";

function Notification({
    message,
    type,
    duration = 3000, // Default duration in milliseconds
    onClose,
}: {
    message: string;
    type: "success" | "error";
    duration?: number;
    onClose?: () => void;
}) {
    const [visible, setVisible] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setVisible(false);
            if (onClose) onClose(); // Trigger the onClose callback if provided
        }, duration);

        return () => clearTimeout(timer); // Clear the timeout if component unmounts
    }, [duration, onClose]);

    if (!visible) return null;

    const bgColor = type === "success" ? "bg-green-500" : "bg-red-500";

    return (
        <div
            className={`fixed top-5 right-5 p-4 text-white ${bgColor} rounded-lg shadow-md transition-opacity duration-300 ease-in-out ${visible ? "opacity-100" : "opacity-0"
                }`}
        >
            {message}
        </div>
    );
}

export default Notification;
