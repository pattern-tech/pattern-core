import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import Notification from "@/components/notification/notification";
import logoBlack from "@/assets/logoBlack.svg";
import { useNavigate } from "react-router-dom";


export function LoginPage() {
    const [formData, setFormData] = useState({
        email: "",
        password: "",
    });

    const [loading, setLoading] = useState(false);
    const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Login failed");
            }

            const data = await response.json();

            localStorage.setItem("token", data.data.access_token);

            setNotification({ message: "Login successful!", type: "success" });
            navigate("/projects");
        } catch (error: any) {
            setNotification({ message: error.message || "An error occurred", type: "error" });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100 relative">
            {/* Notification */}
            {notification && (
                <Notification
                    message={notification.message}
                    type={notification.type}
                    onClose={() => setNotification(null)} // Clear the notification state
                />
            )}

            {/* Registration Form */}
            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
                {/* Logo */}
                <div className="flex justify-center mb-6">
                    <img src={logoBlack} alt="Logo" className="h-12" />
                </div>
                <h1 className="text-2xl font-bold text-center mb-6">Login</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="email" className="block text-sm font-medium">
                            Email
                        </label>
                        <Input
                            id="email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Enter your email"
                            required
                        />
                    </div>
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium">
                            Password
                        </label>
                        <Input
                            id="password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter your password"
                            required
                        />
                    </div>
                    <Button type="submit" className="w-full" disabled={loading}>
                        {loading ? "Login..." : "Login"}
                    </Button>
                </form>
                <div className="text-center mt-4">
                    <p className="text-sm">
                        Don't have an account?{" "}
                        <a href="/register" className="text-blue-500 hover:underline">
                            Create one
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );
}
