import { Dialog, DialogPanel } from "@headlessui/react";

export function Modal({ isOpen, onClose, children }: ModalProps) {
    return (
        <Dialog open={isOpen} onClose={onClose} className="fixed inset-0 z-50">
            <div className="flex items-center justify-center min-h-screen bg-black bg-opacity-50">
                <DialogPanel className="relative bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 text-gray-500 hover:text-gray-800"
                        aria-label="Close"
                    >
                        ✕
                    </button>
                    {children}
                </DialogPanel>
            </div>
        </Dialog>
    );
}

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
}
