import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { fetchClient } from "@/utils/fetchClient";
import Notification from "@/components/notification/notification";
import { useParams } from "react-router-dom";

interface Tool {
    id: string;
    name: string;
    description: string;
}



export function ProjectTools() {
    const { projectId } = useParams();

    const [notification, setNotification] = useState<{ message: string; type: "success" | "error" } | null>(null);
    const [tools, setTools] = useState<Tool[]>([]);
    const [toolsTotalCount, setToolsTotalCount] = useState(0);
    const [selectedTools, setSelectedTools] = useState<string[]>([]);
    const [isToolModalOpen, setIsToolModalOpen] = useState(false);

    const [projectTools, setProjectTools] = useState<Tool[]>([]);
    const [projectToolsTotalCount, setProjectToolsTotalCount] = useState(0);

    const [query, setQuery] = useState("");
    const [offset, setOffset] = useState(0);
    const [selectedOffset, setSelectedOffset] = useState(0);
    const limit = 10;
    const selectedLimit = 10;

    useEffect(() => {
        fetchProjectTools(selectedOffset);
    }, [selectedOffset]);

    const fetchProjectTools = async (currentOffset: number) => {
        try {
            const url = `/project/${projectId}/tools?limit=${selectedLimit}&offset=${currentOffset}`;
            const response = await fetchClient(url);

            setProjectTools(response.data);
            setProjectToolsTotalCount(response.metadata.total_count);
        } catch (error) {
            console.error("Failed to fetch project tools:", error);
        }
    };

    const fetchTools = async (searchQuery: string = "", currentOffset: number = 0) => {
        try {
            const url = `/tool/?query=${encodeURIComponent(searchQuery)}&limit=${limit}&offset=${currentOffset}`;
            const response = await fetchClient(url);

            // Assuming response.data = {items: Tool[], total_count: number}
            setTools(response.data);
            setToolsTotalCount(response.metadata.total_count);
        } catch (error) {
            console.error("Failed to fetch tools:", error);
        }
    };

    const handleAddTools = async () => {
        try {
            await fetchClient("/project/tools", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer your-jwt-token",
                },
                body: JSON.stringify({
                    project_id: projectId,
                    tools_id: selectedTools,
                }),
            });

            setNotification({ message: "Tools added successfully!", type: "success" });
            setIsToolModalOpen(false);
            setSelectedTools([]);
            fetchProjectTools(selectedOffset);
        } catch (error) {
            setNotification({ message: "Failed to add tools", type: "error" });
            console.error("Failed to add tools:", error);
        }
    };

    const toggleToolSelection = (toolId: string) => {
        setSelectedTools((prevSelected) =>
            prevSelected.includes(toolId)
                ? prevSelected.filter((id) => id !== toolId)
                : [...prevSelected, toolId]
        );
    };

    const openToolModal = () => {
        setOffset(0);
        setQuery("");
        fetchTools("", 0);
        setIsToolModalOpen(true);
    };

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newQuery = e.target.value;
        setQuery(newQuery);
        setOffset(0);
        fetchTools(newQuery, 0);
    };

    const handleNext = () => {
        const newOffset = offset + limit;
        if (newOffset < toolsTotalCount) {
            setOffset(newOffset);
            fetchTools(query, newOffset);
        }
    };

    const handlePrev = () => {
        const newOffset = Math.max(0, offset - limit);
        setOffset(newOffset);
        fetchTools(query, newOffset);
    };

    const handleSelectedNext = () => {
        const newOffset = selectedOffset + selectedLimit;
        if (newOffset < projectToolsTotalCount) {
            setSelectedOffset(newOffset);
        }
    };

    const handleSelectedPrev = () => {
        const newOffset = Math.max(0, selectedOffset - selectedLimit);
        setSelectedOffset(newOffset);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Project Tools</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {notification && (
                    <Notification
                        message={notification.message}
                        type={notification.type}
                        onClose={() => setNotification(null)} // Clear the notification state
                    />
                )}

                <Button onClick={openToolModal}>
                    Add New Tools
                </Button>

                {/* Display the list of tools already associated with the project in a table */}
                <h3 className="text-xl font-semibold mt-4">Selected Tools</h3>
                {projectTools?.length === 0 ? (
                    <p>No tools have been added to this project yet.</p>
                ) : (
                    <>
                        <table className="w-full border-collapse border border-gray-300 mt-2">
                            <thead>
                                <tr className="bg-gray-100 border-b border-gray-300">
                                    <th className="p-2 text-left">Name</th>
                                    <th className="p-2 text-left">Description</th>
                                    <th className="p-2 text-left">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {projectTools.map((tool) => (
                                    <tr key={tool.id} className="border-b border-gray-300">
                                        <td className="p-2">{tool.name}</td>
                                        <td className="p-2">{tool.description}</td>
                                        <td className="p-2">

                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div className="flex justify-between items-center mt-4">
                            <Button variant="outline" onClick={handleSelectedPrev} disabled={selectedOffset === 0}>
                                Previous
                            </Button>
                            <div>
                                Page {Math.floor(selectedOffset / selectedLimit) + 1} of {Math.ceil(projectToolsTotalCount / selectedLimit)}
                            </div>
                            <Button
                                variant="outline"
                                onClick={handleSelectedNext}
                                disabled={selectedOffset + selectedLimit >= projectToolsTotalCount}
                            >
                                Next
                            </Button>
                        </div>
                    </>
                )}

                {/* Modal for adding new tools */}
                {isToolModalOpen && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
                        <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold">Select Tools</h2>
                                <Button variant="secondary" onClick={() => setIsToolModalOpen(false)}>
                                    Close
                                </Button>
                            </div>
                            <div className="mb-4">
                                <input
                                    type="text"
                                    className="border border-gray-300 rounded p-2 w-full"
                                    placeholder="Search tools..."
                                    value={query}
                                    onChange={handleSearch}
                                />
                            </div>

                            {tools.length === 0 ? (
                                <p>No available tools to add.</p>
                            ) : (
                                <div className="border border-gray-200 rounded mb-4 overflow-auto max-h-100">
                                    <table className="w-full">
                                        <thead className="bg-gray-100">
                                            <tr>
                                                <th className="p-2 text-left">Select</th>
                                                <th className="p-2 text-left">Name</th>
                                                <th className="p-2 text-left">Description</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {tools.map((tool) => (
                                                <tr key={tool.id} className="border-b border-gray-200">
                                                    <td className="p-2">
                                                        <input
                                                            type="checkbox"
                                                            checked={selectedTools.includes(tool.id)}
                                                            onChange={() => toggleToolSelection(tool.id)}
                                                        />
                                                    </td>
                                                    <td className="p-2">{tool.name}</td>
                                                    <td className="p-2">{tool.description}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            <div className="flex justify-between items-center mb-4">
                                <div className="flex space-x-2">
                                    <Button
                                        variant="outline"
                                        onClick={handlePrev}
                                        disabled={offset === 0}
                                    >
                                        Previous
                                    </Button>
                                    <Button
                                        variant="outline"
                                        onClick={handleNext}
                                        disabled={offset + limit >= toolsTotalCount}
                                    >
                                        Next
                                    </Button>
                                </div>
                                <div>
                                    Page {Math.floor(offset / limit) + 1} of {Math.ceil(toolsTotalCount / limit)}
                                </div>
                                <Button
                                    onClick={handleAddTools}
                                    disabled={selectedTools.length === 0}
                                >
                                    Add Selected Tools
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

            </CardContent>
        </Card>
    );
}
