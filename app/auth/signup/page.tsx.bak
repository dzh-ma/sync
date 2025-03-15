// signup/page.tsx
"use client"
import Image from "next/image"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { Eye, EyeOff, Mail, User, MapPin, ArrowLeft } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import axios from "axios"
import PhoneInput from "react-phone-input-2"
import "react-phone-input-2/lib/style.css"
import { getNames, getCode } from "country-list"

// Base API URL with fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export default function SignupPage() {
  const { toast } = useToast()
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [verificationCode, setVerificationCode] = useState(["", "", "", "", "", ""])
  const [countries, setCountries] = useState([])
  const [cities, setCities] = useState([])
  const [loadingCities, setLoadingCities] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
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
  })

  const dayOptions = Array.from({ length: 31 }, (_, i) => ({
    value: String(i + 1),
    label: i + 1
  }))

  const monthOptions = Array.from({ length: 12 }, (_, i) => ({
    value: String(i + 1),
    label: i + 1
  }))

  const currentYear = new Date().getFullYear()
  const yearOptions = Array.from({ length: 100 }, (_, i) => ({
    value: String(currentYear - i),
    label: currentYear - i
  }))

  useEffect(() => {
    const countryNames = getNames()
    const countryOptions = countryNames.map((name) => ({
      value: getCode(name),
      label: name
    }))
    setCountries(countryOptions.sort((a, b) => a.label.localeCompare(b.label)))
  }, [])

  useEffect(() => {
    const fetchCities = async () => {
      if (formData.country) {
        setLoadingCities(true)
        try {
          const response = await axios.get(
            `https://api.geonames.org/searchJSON?country=${formData.country}&featureClass=P&maxRows=100&population=100000&username=demo`
          )
          const cityOptions = response.data.geonames
            .map((city) => ({
              value: city.name,
              label: city.name
            }))
            .sort((a, b) => a.label.localeCompare(b.label))
          setCities(cityOptions)
        } catch (error) {
          console.error("Error fetching cities:", error)
          toast({
            title: "Error",
            description: "Failed to fetch cities. Please try again.",
            variant: "destructive"
          })
          // Fallback to empty array if API fails
          setCities([])
        }
        setLoadingCities(false)
      }
    }
    
    if (formData.country) {
      fetchCities()
    }
  }, [formData.country, toast])

  const handleVerificationCodeChange = (index, value) => {
    // Only accept digits
    if (!/^\d*$/.test(value) && value !== "") return
    
    // Limit to one character per input
    if (value.length > 1) return
    
    const newCode = [...verificationCode]
    newCode[index] = value
    setVerificationCode(newCode)

    // Auto-focus next input when a digit is entered
    if (value && index < 5) {
      const nextInput = document.getElementById(`code-${index + 1}`)
      nextInput?.focus()
    }
  }

  const validatePassword = (password) => {
    // Match the backend password validation requirements
    if (password.length < 8) return "Password must be at least 8 characters long."
    if (!/\d/.test(password)) return "Password must contain at least 1 number."
    if (!/[a-z]/.test(password)) return "Password must contain at least 1 lowercase letter."
    if (!/[A-Z]/.test(password)) return "Password must contain at least 1 uppercase letter."
    if (!/[!@#$%^&*()_+\-=\[\]{}|;':",.<>?/]/.test(password)) return "Password must contain at least 1 special character."
    return null
  }

  const handleRegister = async () => {
    // Validate email
    if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address.",
        variant: "destructive"
      })
      return
    }

    // Validate password
    const passwordError = validatePassword(formData.password)
    if (passwordError) {
      toast({
        title: "Invalid Password",
        description: passwordError,
        variant: "destructive"
      })
      return
    }

    // Check if passwords match
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Passwords Don't Match",
        description: "Please ensure that your passwords match.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      // Register the new user using the FastAPI endpoint
      await axios.post(`${API_URL}/users/register`, {
        email: formData.email,
        password: formData.password,
        role: "user" // Default role is user
      })
      
      toast({
        title: "Registration Initiated",
        description: "A verification code has been sent to your email.",
      })
      
      setStep(2)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Registration failed. Please try again."
      toast({
        title: "Registration Failed",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerifyOtp = async () => {
    const otp = verificationCode.join("")
    
    // Validate OTP format
    if (otp.length !== 6 || !/^\d+$/.test(otp)) {
      toast({
        title: "Invalid Code",
        description: "Please enter a valid 6-digit verification code.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      // Verify email using the backend endpoint
      await axios.post(`${API_URL}/users/verify`, {
        email: formData.email,
        code: otp
      })
      
      toast({
        title: "Email Verified",
        description: "Your email has been successfully verified.",
      })
      
      setStep(3)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Verification failed. Please check the code and try again."
      toast({
        title: "Verification Failed",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleResendOtp = async () => {
    setIsLoading(true)
    
    try {
      // Request a new verification code from the backend
      await axios.post(`${API_URL}/users/resend-verification`, {
        email: formData.email
      })
      
      toast({
        title: "Verification Code Resent",
        description: "A new verification code has been sent to your email.",
      })
      
      // Reset the verification code inputs
      setVerificationCode(["", "", "", "", "", ""])
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Failed to resend verification code. Please try again."
      toast({
        title: "Request Failed",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const validateBirthdate = () => {
    const dayNum = parseInt(formData.birthDay, 10)
    const monthNum = parseInt(formData.birthMonth, 10)
    const yearNum = parseInt(formData.birthYear, 10)
    const currentDate = new Date()
    const currentYear = currentDate.getFullYear()

    const errors = {}

    if (isNaN(dayNum) || dayNum < 1 || dayNum > 31) {
      errors.day = "Day must be between 1 and 31"
    }

    if (isNaN(monthNum) || monthNum < 1 || monthNum > 12) {
      errors.month = "Month must be between 1 and 12"
    }

    if (yearNum > currentYear) {
      errors.year = "Year cannot be in the future"
    } else if (yearNum < 1900) {
      errors.year = "Year must be after 1900"
    }

    // Calculate age
    const birthDate = new Date(yearNum, monthNum - 1, dayNum)
    const ageDate = new Date(Date.now() - birthDate.getTime())
    const age = Math.abs(ageDate.getUTCFullYear() - 1970)
    
    if (age < 18) {
      errors.age = "You must be at least 18 years old"
    }

    return errors
  }

  const handleNextToStep5 = () => {
    // Validate required fields
    if (!formData.gender) {
      toast({
        title: "Gender Required",
        description: "Please select your gender.",
        variant: "destructive"
      })
      return
    }
    
    // Validate birthdate
    const errors = validateBirthdate()
    if (Object.keys(errors).length > 0) {
      Object.entries(errors).forEach(([key, message]) => {
        toast({
          title: `${key.charAt(0).toUpperCase() + key.slice(1)} Error`,
          description: message,
          variant: "destructive"
        })
      })
      return
    }
    
    setStep(5)
  }

  const handleCompleteRegistration = async () => {
    // Validate required location fields
    if (!formData.country || !formData.city || !formData.address.trim()) {
      toast({
        title: "Missing Information",
        description: "Please fill in all location fields.",
        variant: "destructive"
      })
      return
    }

    setIsLoading(true)

    try {
      // Create a complete profile by updating the user's profile
      const profileData = {
        user_id: formData.email, // Use email as identifier
        name: `${formData.firstName} ${formData.lastName}`,
        age: String(currentYear - parseInt(formData.birthYear)),
        profile_type: "adult", // Default profile type
        accessibility_settings: {
          preferred_language: "english",
          text_size: "normal",
        },
        can_control_devices: true,
        can_access_energy_data: true,
        can_manage_notifications: true,
        additional_info: {
          first_name: formData.firstName,
          last_name: formData.lastName,
          phone_number: formData.phoneNumber,
          gender: formData.gender,
          birthdate: {
            day: formData.birthDay,
            month: formData.birthMonth,
            year: formData.birthYear
          },
          address: {
            country: formData.country,
            city: formData.city,
            street_address: formData.address
          }
        }
      }
      
      // Create user profile
      await axios.post(`${API_URL}/profiles/create`, profileData)
      
      toast({
        title: "Registration Complete",
        description: "Your account has been created successfully!",
      })
      
      // Redirect to login page
      router.push("/auth/login")
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Failed to complete registration. Please try again."
      toast({
        title: "Registration Failed",
        description: errorMessage,
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

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
              <p className="text-xs text-gray-500">
                Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters.
              </p>
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

            <Button 
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" 
              onClick={handleRegister}
              disabled={isLoading}
            >
              {isLoading ? "Processing..." : "Next"}
            </Button>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">Verify Your Email</h3>
            <p className="text-sm text-gray-500">We've sent a 6-digit verification code to {formData.email}</p>

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
                  className="w-10 h-12 text-center text-xl"
                />
              ))}
            </div>

            <p className="text-sm text-center">
              Didn't receive the code?{" "}
              <button
                className="text-[#00B2FF] hover:underline"
                onClick={handleResendOtp}
                disabled={isLoading}
              >
                Resend verification code
              </button>
            </p>

            <Button 
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" 
              onClick={handleVerifyOtp}
              disabled={isLoading}
            >
              {isLoading ? "Verifying..." : "Verify & Continue"}
            </Button>
          </div>
        )

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
                    required
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
                    required
                  />
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Phone Number</Label>
                <PhoneInput
                  country={"us"}
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

            <Button 
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg" 
              onClick={() => setStep(4)}
              disabled={!formData.firstName || !formData.lastName || !formData.phoneNumber}
            >
              Next
            </Button>
          </div>
        )

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
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other">Other</Label>
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
        )

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
                  onValueChange={(value) => setFormData({ ...formData, country: value, city: "" })}
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
                {loadingCities ? (
                  <div className="h-10 flex items-center justify-center bg-muted rounded-md">
                    <p className="text-sm text-muted-foreground">Loading cities...</p>
                  </div>
                ) : (
                  cities.length > 0 ? (
                    <Select
                      value={formData.city}
                      onValueChange={(value) => setFormData({ ...formData, city: value })}
                      disabled={!formData.country}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Choose your city" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map((city) => (
                          <SelectItem key={city.value} value={city.value}>
                            {city.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      placeholder="Enter your city"
                      disabled={!formData.country}
                    />
                  )
                )}
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
              onClick={handleCompleteRegistration}
              disabled={isLoading}
            >
              {isLoading ? "Completing Registration..." : "Complete Registration"}
            </Button>
          </div>
        )

      default:
        return null
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:flex-1 relative">
        <Image
          src="https://media.istockphoto.com/id/1219569858/photo/woman-cooking-on-the-modern-kitchen-at-home.jpg?s=612x612&w=0&k=20&c=oUTIUAb0_cALWZ2GCTI3ZUmZCH31cf0UmBMPf1tMsck="
          alt="Smart Home"
          fill
          className="object-cover"
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
          <div className="flex justify-between items-center mb-8">
            {step > 1 && (
              <button 
                onClick={handleBack} 
                className="text-[#00B2FF] hover:underline flex items-center"
                disabled={isLoading}
              >
                <ArrowLeft className="mr-2" size={16} />
                Back
              </button>
            )}
            <div className="flex items-center gap-2 ml-auto">
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
  )
}
