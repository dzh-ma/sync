"use client"

import React from "react";
import Image from "next/image"
import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom";
import { Button } from "../../../components/ui/button"
import { Input } from "../../../components/ui/input"
import { Label } from "../../../components/ui/label"
import Link from "next/link"
import { Eye, EyeOff, Mail, User, MapPin, ArrowLeft } from "lucide-react"
import { useToast } from "../../../components/ui/use-toast"
import { RadioGroup, RadioGroupItem } from "../../../components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select"
import axios from "axios"
import PhoneInput from "react-phone-input-2"
import "react-phone-input-2/lib/style.css"
import { getNames, getCode } from "country-list"

const API_URL = "http://localhost:8000";

// Define interfaces for structured data
interface LocationOption {
  value: string;
  label: string;
}

interface PersonalDetails {
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
  gender: string;
  birthdate: {
    day: number;
    month: number;
    year: number;
  };
  country: string;
  city: string;
  address: string;
}

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  phoneNumber: string;
  gender: string;
  birthDay: string;
  birthMonth: string;
  birthYear: string;
  country: string;
  city: string;
  address: string;
}

interface BirthdateErrors {
  day?: string;
  month?: string;
  year?: string;
  age?: string;
}

// API functions
const registerUser = async (email: string, password: string) => {
  return axios.post(`${API_URL}/register`, { email, password });
};

const requestOtp = async (email: string) => {
  return axios.post(`${API_URL}/request-otp`, { email });
};

const verifyOtp = async (email: string, otp: string) => {
  return axios.post(`${API_URL}/verify-otp`, { email, otp });
};

const registerPersonalDetails = async (details: PersonalDetails) => {
  return axios.post(`${API_URL}/register_personal`, details);
};

export default function SignupPage() {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [verificationCode, setVerificationCode] = useState<string[]>(["", "", "", "", ""]);
  const [countries, setCountries] = useState<LocationOption[]>([]);
  const [cities, setCities] = useState<LocationOption[]>([]);
  const [loadingCities, setLoadingCities] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    phoneNumber: "",
    gender: "",
    birthDay: "",
    birthMonth: "",
    birthYear: "",
    country: "",
    city: "",
    address: "",
  });

  const dayOptions: LocationOption[] = Array.from({ length: 31 }, (_, i) => ({
    value: String(i + 1),
    label: String(i + 1)
  }));

  const monthOptions: LocationOption[] = Array.from({ length: 12 }, (_, i) => ({
    value: String(i + 1),
    label: String(i + 1)
  }));

  const currentYear = new Date().getFullYear();
  const yearOptions: LocationOption[] = Array.from({ length: 100 }, (_, i) => ({
    value: String(currentYear - i),
    label: String(currentYear - i)
  }));

  useEffect(() => {
    const countryNames = getNames();
    const countryOptions: LocationOption[] = countryNames.map((name) => ({
      value: getCode(name) || "",
      label: name
    }));
    setCountries(countryOptions.sort((a, b) => a.label.localeCompare(b.label)));
  }, []);

  useEffect(() => {
    const fetchCities = async () => {
      if (formData.country) {
        setLoadingCities(true);
        try {
          const response = await axios.get(
            `http://api.geonames.org/searchJSON?country=${formData.country}&featureClass=P&maxRows=100&population=100000&username=mu50n`
          );
          const cityOptions: LocationOption[] = response.data.geonames
            .map((city: any) => ({
              value: city.name,
              label: city.name
            }))
            .sort((a: LocationOption, b: LocationOption) => a.label.localeCompare(b.label));
          setCities(cityOptions);
        } catch (error) {
          console.error("Error fetching cities:", error);
          toast({
            title: "Error",
            description: "Failed to fetch cities. Please try again.",
            variant: "destructive"
          });
        }
        setLoadingCities(false);
      }
    };
    fetchCities();
  }, [formData.country, toast]);

  const handleVerificationCodeChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const newCode = [...verificationCode];
    newCode[index] = value;
    setVerificationCode(newCode);

    if (value && index < 4) {
      const nextInput = document.getElementById(`code-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleRegister = async () => {
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Passwords do not match",
        description: "Please ensure that your passwords match.",
        variant: "destructive"
      });
      return;
    }

    try {
      await registerUser(formData.email, formData.password);
      await requestOtp(formData.email);
      setStep(2);
    } catch (error: any) {
      toast({
        title: "Registration Failed",
        description: error.response?.data?.detail || "An error occurred.",
        variant: "destructive"
      });
    }
  };

  const handleVerifyOtp = async () => {
    try {
      const otp = verificationCode.join("");
      await verifyOtp(formData.email, otp);
      setStep(3);
    } catch (error: any) {
      toast({
        title: "OTP Verification Failed",
        description: error.response?.data?.detail || "An error occurred.",
        variant: "destructive"
      });
    }
  };

  const handleResendOtp = async () => {
    try {
      await requestOtp(formData.email);
      toast({
        title: "OTP Resent",
        description: "A new OTP has been sent to your email.",
        variant: "default"
      });
    } catch (error: any) {
      toast({
        title: "Failed to Resend OTP",
        description: error.response?.data?.detail || "An error occurred.",
        variant: "destructive"
      });
    }
  };

  const handleRegisterPersonalDetails = async () => {
    if (!formData.address.trim()) {
      toast({
        title: "Invalid Address",
        description: "Address is required",
        variant: "destructive"
      });
      return;
    }

    try {
      const details: PersonalDetails = {
        email: formData.email,
        firstName: formData.firstName,
        lastName: formData.lastName,
        phoneNumber: formData.phoneNumber,
        gender: formData.gender,
        birthdate: {
          day: parseInt(formData.birthDay, 10),
          month: parseInt(formData.birthMonth, 10),
          year: parseInt(formData.birthYear, 10)
        },
        country: formData.country,
        city: formData.city,
        address: formData.address
      };
      await registerPersonalDetails(details);
      toast({
        title: "Registration Complete",
        description: "Your account has been created successfully."
      });
      navigate("/");
    } catch (error: any) {
      toast({
        title: "Registration Failed",
        description: error.response?.data?.detail || "An error occurred.",
        variant: "destructive"
      });
    }
  };

  const validateBirthdate = (): BirthdateErrors => {
    const dayNum = parseInt(formData.birthDay, 10);
    const monthNum = parseInt(formData.birthMonth, 10);
    const yearNum = parseInt(formData.birthYear, 10);
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();

    const errors: BirthdateErrors = {};

    if (isNaN(dayNum) || dayNum < 1 || dayNum > 31) {
      errors.day = "Day must be between 1 and 31";
    }

    if (isNaN(monthNum) || monthNum < 1 || monthNum > 12) {
      errors.month = "Month must be between 1 and 12";
    }

    if (yearNum > currentYear) {
      errors.year = "Year cannot be in the future";
    } else if (yearNum < 1900) {
      errors.year = "Year must be after 1900";
    }

    const age = currentYear - yearNum;
    if (age < 18) {
      errors.age = "You must be at least 18 years old";
    }

    return errors;
  };

  const handleNextToStep5 = () => {
    const errors = validateBirthdate();
    if (Object.keys(errors).length > 0) {
      Object.entries(errors).forEach(([key, message]) => {
        toast({
          title: `${key.charAt(0).toUpperCase() + key.slice(1)} Error`,
          description: message,
          variant: "destructive"
        });
      });
    } else {
      setStep(5);
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="space-y-2">
              <Label>Enter your Email</Label>
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
              <Label>Password</Label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="pr-10"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Confirm Password</Label>
              <div className="relative">
                <Input
                  type={showConfirmPassword ? "text" : "password"}
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="pr-10"
                  placeholder="Confirm your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <Button className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" onClick={handleRegister}>
              Next
            </Button>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Verify Your Email</h3>
            <p className="text-sm text-gray-500">Please Enter The Code We Sent to your email</p>

            <div className="flex justify-between gap-2">
              {verificationCode.map((digit, index) => (
                <Input
                  key={index}
                  id={`code-${index}`}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleVerificationCodeChange(index, e.target.value)}
                  className="w-12 h-12 text-center text-2xl"
                />
              ))}
            </div>

            <p className="text-sm text-center">
              I did not receive the code.{" "}
              <button
                className="text-[#00B2FF] hover:underline"
                onClick={handleResendOtp}
              >
                Resend the code
              </button>
            </p>

            <Button className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" onClick={handleVerifyOtp}>
              Next
            </Button>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Personal Details</h3>
            <p className="text-sm text-gray-500">Fill in your personal information</p>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>First Name</Label>
                <div className="relative">
                  <Input
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    placeholder="Enter your First Name"
                    className="pl-10"
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Last Name</Label>
                <div className="relative">
                  <Input
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    placeholder="Enter your Last Name"
                    className="pl-10"
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Phone Number</Label>
                <PhoneInput
                  country={"ae"}
                  value={formData.phoneNumber}
                  onChange={(phone) => setFormData({ ...formData, phoneNumber: phone })}
                  inputClass="!w-full !py-2 !px-3 !text-base !h-10 !rounded-md !border-input"
                  containerClass="!w-full"
                  buttonClass="!border-input !bg-background !rounded-l-md !h-10 !w-12"
                  dropdownClass="!bg-background !text-foreground"
                  searchClass="!bg-background !text-foreground"
                />
              </div>
            </div>

            <Button className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" onClick={() => setStep(4)}>
              Next
            </Button>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Additional Details</h3>
            <p className="text-sm text-gray-500">Please provide your gender and birthdate</p>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Gender</Label>
                <RadioGroup
                  value={formData.gender}
                  onValueChange={(value) => setFormData({ ...formData, gender: value })}
                  className="flex gap-4"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">Male</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">Female</Label>
                  </div>
                </RadioGroup>
              </div>

              <div className="space-y-2">
                <Label>Birthdate</Label>
                <div className="flex gap-4">
                  <Select
                    value={formData.birthDay}
                    onValueChange={(value) => setFormData({ ...formData, birthDay: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Day" />
                    </SelectTrigger>
                    <SelectContent>
                      {dayOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={formData.birthMonth}
                    onValueChange={(value) => setFormData({ ...formData, birthMonth: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Month" />
                    </SelectTrigger>
                    <SelectContent>
                      {monthOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={formData.birthYear}
                    onValueChange={(value) => setFormData({ ...formData, birthYear: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Year" />
                    </SelectTrigger>
                    <SelectContent>
                      {yearOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <Button
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg"
              onClick={handleNextToStep5}
            >
              Next
            </Button>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Location Details</h3>
            <p className="text-sm text-gray-500">Fill in your location information</p>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Country</Label>
                <Select
                  value={formData.country}
                  onValueChange={(value) => setFormData({ ...formData, country: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose your country" />
                  </SelectTrigger>
                  <SelectContent>
                    {countries.map((country) => (
                      <SelectItem key={country.value} value={country.value}>
                        {country.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>City</Label>
                <Select
                  value={formData.city}
                  onValueChange={(value) => setFormData({ ...formData, city: value })}
                  disabled={loadingCities || !formData.country}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={loadingCities ? "Loading cities..." : "Choose your city"} />
                  </SelectTrigger>
                  <SelectContent>
                    {cities.map((city) => (
                      <SelectItem key={city.value} value={city.value}>
                        {city.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Address</Label>
                <div className="relative">
                  <Input
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    placeholder="Enter your address"
                    className="pl-10"
                  />
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>
            </div>

            <Button
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg"
              onClick={handleRegisterPersonalDetails}
            >
              Finish
            </Button>
          </div>
        );

      default:
        return null;
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
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
            <span className="text-[#00B2FF]">SYNC</span>
          </h1>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex justify-between items-center mb-8">
            {step > 1 && (
              <button onClick={handleBack} className="text-[#00B2FF] hover:underline flex items-center">
                <ArrowLeft className="mr-2" size={16} />
                Back
              </button>
            )}
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold bg-[#00B2FF] text-white px-3 py-1 rounded-full">
                Sy<span className="text-[#FFB800]">nc</span>
              </span>
            </div>
          </div>

          {renderStep()}

          {step === 1 && (
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{" "}
                <Link href="/auth/login" className="text-[#00B2FF] hover:underline">
                  Login Here
                </Link>
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
