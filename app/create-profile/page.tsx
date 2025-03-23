"use client";

import { useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, Users } from "lucide-react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { motion } from "framer-motion";
import { toast } from "@/components/ui/use-toast";
import axios from "axios";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";

// Define avatar options
const AVATAR_OPTIONS = {
    male: ["/avatar1.jpg", "/avatar2.jpg", "/avatar3.png"],
    female: ["/avatar4.jpg", "/avatar5.jpg", "/avatar6.jpg"],
    child: ["/avatar7.jpg", "/avatar8.jpg"],
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function CreateProfilePage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [isAvatarDialogOpen, setIsAvatarDialogOpen] = useState(false);
    const [formData, setFormData] = useState({
        profileType: "",
        role: "",
        firstName: "",
        lastName: "",
        email: "",
        age: "",
        energyGoal: "",
        accessibility: false,
        avatar: "",
        pinType: "admin", // "admin" or "user"
        pin: ["", "", "", ""],
        permissions: {
            notifications: true,
            energyAlerts: true,
            addAutomation: false,
            statisticalData: false,
            deviceControl: true,
            roomControl: false,
        },
    });

    const handlePinChange = (index: number, value: string) => {
        if (value.length > 1) return; // Only allow single digits
        const newPin = [...formData.pin];
        newPin[index] = value;
        setFormData({ ...formData, pin: newPin });

        // Auto-focus next input
        if (value !== "" && index < 3) {
            const nextInput = document.getElementById(`pin-${index + 1}`);
            nextInput?.focus();
        }
    };

    const handleAvatarSelect = (avatar: string) => {
        setFormData({ ...formData, avatar });
        setIsAvatarDialogOpen(false);
    };

    const handleSubmit = async () => {
        const pin = formData.pin.join("");
        const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");

        if (!formData.firstName || !formData.lastName || !formData.email || !formData.role) {
            toast({
                title: "Missing Information",
                description: "Please fill in all required fields.",
                variant: "destructive",
            });
            return;
        }

        if (formData.pinType === "admin" && pin.length !== 4) {
            toast({
                title: "Invalid PIN",
                description: "Please enter a 4-digit PIN.",
                variant: "destructive",
            });
            return;
        }

        const payload = {
            name: `${formData.firstName} ${formData.lastName}`,
            email: formData.email,
            account_type: formData.role,
            pin_option: formData.pinType,
            household_id: currentUser.householdId,
            admin_user: currentUser.email,
            pin: pin,
            permissions: formData.permissions,
        };

        try {
            await axios.post(`${API_URL}/api/create-profile`, payload);

            toast({
                title: "Profile Created",
                description: "The new household member profile has been successfully created.",
            });
            router.push("/profile");
        } catch (error) {
            console.error("Error creating profile:", error);
            toast({
                title: "Error",
                description: "Failed to create profile. Please try again.",
                variant: "destructive",
            });
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <header className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" size="icon" onClick={() => router.back()}>
                            <ArrowLeft className="h-6 w-6" />
                        </Button>
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                                <Users className="h-6 w-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-800">Create Profile</h1>
                                <p className="text-sm text-gray-500">Add a new family member or guest</p>
                            </div>
                        </div>
                    </div>
                </header>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle>
                            {step === 1
                                ? "Profile Information"
                                : step === 2
                                ? "Set PIN Code"
                                : "Set Permissions"}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        {step === 1 && (
                            <div className="grid grid-cols-2 gap-6">
                                <div className="col-span-2">
                                    <Label>Select Profile Type</Label>
                                    <Select
                                        value={formData.profileType}
                                        onValueChange={(value) =>
                                            setFormData({ ...formData, profileType: value })
                                        }
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select profile type" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="family">Family Member</SelectItem>
                                            <SelectItem value="guest">Guest</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="col-span-2">
                                    <Label>Select Role</Label>
                                    <Select
                                        value={formData.role}
                                        onValueChange={(value) =>
                                            setFormData({ ...formData, role: value })
                                        }
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select role" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="adult">Adult</SelectItem>
                                            <SelectItem value="child">Child</SelectItem>
                                            <SelectItem value="admin">Admin</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div>
                                    <Label>First Name</Label>
                                    <Input
                                        value={formData.firstName}
                                        onChange={(e) =>
                                            setFormData({ ...formData, firstName: e.target.value })
                                        }
                                    />
                                </div>

                                <div>
                                    <Label>Last Name</Label>
                                    <Input
                                        value={formData.lastName}
                                        onChange={(e) =>
                                            setFormData({ ...formData, lastName: e.target.value })
                                        }
                                    />
                                </div>

                                <div className="col-span-2">
                                    <Label>Email Address</Label>
                                    <Input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) =>
                                            setFormData({ ...formData, email: e.target.value })
                                        }
                                    />
                                </div>

                                <div>
                                    <Label>Age</Label>
                                    <Input
                                        type="number"
                                        value={formData.age}
                                        onChange={(e) =>
                                            setFormData({ ...formData, age: e.target.value })
                                        }
                                    />
                                </div>

                                <div>
                                    <Label>Energy Saving Goal (kWh)</Label>
                                    <Input
                                        type="number"
                                        value={formData.energyGoal}
                                        onChange={(e) =>
                                            setFormData({ ...formData, energyGoal: e.target.value })
                                        }
                                    />
                                </div>

                                <div className="col-span-2">
                                    <div className="flex items-center justify-between">
                                        <Label>Accessibility features</Label>
                                        <Switch
                                            checked={formData.accessibility}
                                            onCheckedChange={(checked) =>
                                                setFormData({ ...formData, accessibility: checked })
                                            }
                                        />
                                    </div>
                                </div>

                                <div className="col-span-2">
                                    <Label>Profile Avatar</Label>
                                    <div className="mt-2 flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-6">
                                        <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mb-4">
                                            {formData.avatar ? (
                                                <Image
                                                    src={formData.avatar}
                                                    alt="Avatar"
                                                    width={96}
                                                    height={96}
                                                    className="rounded-full object-cover"
                                                />
                                            ) : (
                                                <span className="text-gray-400">No avatar</span>
                                            )}
                                        </div>
                                        <Button
                                            variant="outline"
                                            onClick={() => setIsAvatarDialogOpen(true)}
                                        >
                                            Select Avatar
                                        </Button>
                                    </div>
                                </div>

                                <div className="col-span-2">
                                    <Button
                                        className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                                        onClick={() => setStep(2)}
                                    >
                                        Next
                                    </Button>
                                </div>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="space-y-6">
                                <div className="space-y-4">
                                    <Label>PIN Setup Method</Label>
                                    <RadioGroup
                                        defaultValue={formData.pinType}
                                        onValueChange={(value) =>
                                            setFormData({ ...formData, pinType: value })
                                        }
                                        className="flex flex-col space-y-2"
                                    >
                                        <div className="flex items-center space-x-2">
                                            <RadioGroupItem value="admin" id="admin" />
                                            <Label htmlFor="admin">I set the PIN</Label>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <RadioGroupItem value="user" id="user" />
                                            <Label htmlFor="user">User sets the PIN</Label>
                                        </div>
                                    </RadioGroup>
                                </div>

                                {formData.pinType === "admin" && (
                                    <div className="space-y-4">
                                        <Label>Enter 4-digit PIN</Label>
                                        <div className="flex justify-center gap-4">
                                            {[0, 1, 2, 3].map((i) => (
                                                <Input
                                                    key={i}
                                                    id={`pin-${i}`}
                                                    type="text"
                                                    inputMode="numeric"
                                                    pattern="[0-9]*"
                                                    maxLength={1}
                                                    className="w-16 h-16 text-2xl text-center"
                                                    value={formData.pin[i]}
                                                    onChange={(e) =>
                                                        handlePinChange(i, e.target.value)
                                                    }
                                                    onKeyDown={(e) => {
                                                        if (
                                                            e.key === "Backspace" &&
                                                            !formData.pin[i] &&
                                                            i > 0
                                                        ) {
                                                            const prevInput =
                                                                document.getElementById(`pin-${i - 1}`);
                                                            prevInput?.focus();
                                                        }
                                                    }}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="flex gap-4">
                                    <Button
                                        variant="outline"
                                        className="flex-1"
                                        onClick={() => setStep(1)}
                                    >
                                        Back
                                    </Button>
                                    <Button
                                        className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                                        onClick={() => setStep(3)}
                                    >
                                        Next
                                    </Button>
                                </div>
                            </div>
                        )}

                        {step === 3 && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold">Set Permissions</h3>
                                {Object.entries(formData.permissions).map(([key, value]) => (
                                    <div key={key} className="flex items-center justify-between">
                                        <Label htmlFor={key} className="flex items-center space-x-2">
                                            <span>
                                                {key
                                                    .replace(/([A-Z])/g, " $1")
                                                    .replace(/^./, (str) => str.toUpperCase())}
                                            </span>
                                        </Label>
                                        <Switch
                                            id={key}
                                            checked={value as boolean}
                                            onCheckedChange={(checked) =>
                                                setFormData({
                                                    ...formData,
                                                    permissions: {
                                                        ...formData.permissions,
                                                        [key]: checked,
                                                    },
                                                })
                                            }
                                            className="data-[state=checked]:bg-[#00B2FF]"
                                        />
                                    </div>
                                ))}
                                <div className="flex gap-4">
                                    <Button
                                        variant="outline"
                                        className="flex-1"
                                        onClick={() => setStep(2)}
                                    >
                                        Back
                                    </Button>
                                    <Button
                                        className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                                        onClick={handleSubmit}
                                    >
                                        Create Profile
                                    </Button>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </motion.div>

            {/* Avatar Selection Dialog */}
            <Dialog open={isAvatarDialogOpen} onOpenChange={setIsAvatarDialogOpen}>
                <DialogContent className="sm:max-w-[600px]">
                    <DialogHeader>
                        <DialogTitle>Select Avatar</DialogTitle>
                        <DialogDescription>Choose a profile avatar</DialogDescription>
                    </DialogHeader>
                    <div className="py-4">
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold mb-2">Male Avatars</h3>
                            <div className="grid grid-cols-3 gap-4">
                                {AVATAR_OPTIONS.male.map((avatar, index) => (
                                    <button
                                        key={`male-${index}`}
                                        onClick={() => handleAvatarSelect(avatar)}
                                        className="flex flex-col items-center gap-2 p-4 border rounded-lg hover:border-[#00B2FF] transition-colors"
                                    >
                                        <Image
                                            src={avatar}
                                            alt={`Male avatar ${index + 1}`}
                                            width={80}
                                            height={80}
                                            className="rounded-full object-cover"
                                        />
                                        <span className="text-sm font-medium">Male {index + 1}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold mb-2">Female Avatars</h3>
                            <div className="grid grid-cols-3 gap-4">
                                {AVATAR_OPTIONS.female.map((avatar, index) => (
                                    <button
                                        key={`female-${index}`}
                                        onClick={() => handleAvatarSelect(avatar)}
                                        className="flex flex-col items-center gap-2 p-4 border rounded-lg hover:border-[#00B2FF] transition-colors"
                                    >
                                        <Image
                                            src={avatar}
                                            alt={`Female avatar ${index + 1}`}
                                            width={80}
                                            height={80}
                                            className="rounded-full object-cover"
                                        />
                                        <span className="text-sm font-medium">Female {index + 1}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold mb-2">Child Avatars</h3>
                            <div className="grid grid-cols-2 gap-4">
                                {AVATAR_OPTIONS.child.map((avatar, index) => (
                                    <button
                                        key={`child-${index}`}
                                        onClick={() => handleAvatarSelect(avatar)}
                                        className="flex flex-col items-center gap-2 p-4 border rounded-lg hover:border-[#00B2FF] transition-colors"
                                    >
                                        <Image
                                            src={avatar}
                                            alt={`Child avatar ${index + 1}`}
                                            width={80}
                                            height={80}
                                            className="rounded-full object-cover"
                                        />
                                        <span className="text-sm font-medium">Child {index + 1}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}