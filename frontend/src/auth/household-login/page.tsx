import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Mail } from "lucide-react";
import { toast } from "../../../components/ui/use-toast";

export default function HouseholdLoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    pin: ["", "", "", ""],
  });

  const handlePinChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const newPin = [...formData.pin];
    newPin[index] = value;
    setFormData({ ...formData, pin: newPin });

    if (value && index < 3) {
      const nextInput = document.getElementById(`pin-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const familyMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]");
    const member = familyMembers.find((m: any) => m.email === formData.email && m.pin === formData.pin.join(""));

    if (member) {
      localStorage.setItem(
        "currentUser",
        JSON.stringify({
          id: member.id,
          type: "household",
          email: member.email,
          name: member.name,
          role: member.role,
          permissions: member.permissions,
        })
      );
      navigate("/");
    } else {
      toast({
        title: "Login Failed",
        description: "Invalid email or PIN. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:flex-1 relative">
        <img
          src="https://media.istockphoto.com/id/1219569858/photo/woman-cooking-on-the-modern-kitchen-at-home.jpg?s=612x612&w=0&k=20&c=oUTIUAb0_cALWZ2GCTI3ZUmZCH31cf0UmBMPf1tMsck="
          alt="Smart Home"
          className="object-cover absolute inset-0 w-full h-full"
        />
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute bottom-20 left-10 text-white">
          <h1 className="text-5xl font-bold mb-4">
            <span className="text-[#00B2FF]">SYNC</span> your Home,
            <br />
            Save energy,
            <br />
            and live smarter.
          </h1>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex justify-end mb-8">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold bg-[#00B2FF] text-white px-3 py-1 rounded-full">
                Sy<span className="text-[#FFB800]">nc</span>
              </span>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold">Welcome,</h2>
            <p className="text-gray-600">Household Member</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Enter your Email</label>
              <div className="relative">
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="pl-10"
                  placeholder="Enter your Email"
                  required
                />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">PIN</label>
              <div className="flex justify-between gap-4">
                {[0, 1, 2, 3].map((i) => (
                  <Input
                    key={i}
                    id={`pin-${i}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={formData.pin[i]}
                    onChange={(e) => handlePinChange(i, e.target.value)}
                    className="w-16 h-16 text-center text-2xl"
                    required
                  />
                ))}
              </div>
            </div>

            <Button type="submit" className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg">
              Login
            </Button>

            <div className="text-center">
              <Link to="/auth/login" className="text-[#00B2FF] hover:underline text-sm">
                ← Back to Admin Login
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
