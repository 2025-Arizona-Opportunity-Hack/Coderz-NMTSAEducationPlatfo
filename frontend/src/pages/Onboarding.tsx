import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GraduationCap, Users, Upload, Check } from "lucide-react";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Card, CardBody } from "@heroui/card";
import { Select, SelectItem } from "@heroui/select";
import { Progress } from "@heroui/progress";

import {
  authService,
  type RoleSelectionData,
  type TeacherOnboardingData,
  type StudentOnboardingData,
} from "../services/auth.service";
import { useAuthStore } from "../store/useAuthStore";

type OnboardingStep = "role" | "profile";

// Textarea component wrapper since @heroui doesn't have a separate textarea package
interface TextareaProps {
  label: string;
  description?: string;
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  rows?: number;
}

function Textarea({
  label,
  description,
  placeholder,
  value,
  onChange,
  rows = 4,
}: TextareaProps) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-foreground-600">{label}</label>
      <textarea
        className="px-3 py-2 rounded-lg border-2 border-default-200 hover:border-default-400 focus:border-primary focus:outline-none transition-colors resize-vertical min-h-[80px]"
        placeholder={placeholder}
        rows={rows}
        value={value}
        onChange={onChange}
      />
      {description && (
        <p className="text-xs text-foreground-400">{description}</p>
      )}
    </div>
  );
}

const RELATIONSHIP_CHOICES = [
  { value: "parent", label: "Parent" },
  { value: "guardian", label: "Guardian" },
  { value: "caregiver", label: "Professional Caregiver" },
  { value: "family", label: "Family Member" },
  { value: "self", label: "Self" },
  { value: "professional", label: "Healthcare Professional" },
  { value: "other", label: "Other" },
];

export function Onboarding() {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();

  const [step, setStep] = useState<OnboardingStep>("role");
  const [selectedRole, setSelectedRole] = useState<
    "student" | "teacher" | null
  >(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // Teacher form state
  const [teacherData, setTeacherData] = useState<TeacherOnboardingData>({
    bio: "",
    credentials: "",
    specialization: "",
    years_experience: undefined,
    resume: undefined,
    certifications: undefined,
  });

  // Student form state
  const [studentData, setStudentData] = useState<StudentOnboardingData>({
    relationship: "",
    care_recipient_name: "",
    care_recipient_age: undefined,
    special_needs: "",
    learning_goals: "",
    interests: "",
    accessibility_needs: "",
  });

  const handleRoleSelect = async (role: "student" | "teacher") => {
    setError("");
    setIsLoading(true);

    try {
      await authService.selectRole({ role } as RoleSelectionData);
      setSelectedRole(role);
      setStep("profile");
    } catch (err: any) {
      setError(err.message || "Failed to select role");
    } finally {
      setIsLoading(false);
    }
  };

  const handleTeacherSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await authService.completeTeacherOnboarding(teacherData);

      if (response.user) {
        setAuth(response.user);
      }

      // Navigate to teacher dashboard
      navigate("/teacher/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.message || "Failed to complete onboarding");
      setIsLoading(false);
    }
  };

  const handleStudentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await authService.completeStudentOnboarding(studentData);

      if (response.user) {
        setAuth(response.user);
      }

      // Navigate to student dashboard
      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setError(err.message || "Failed to complete onboarding");
      setIsLoading(false);
    }
  };

  const handleFileChange = (
    field: "resume" | "certifications",
    file: File | null,
  ) => {
    setTeacherData((prev) => ({
      ...prev,
      [field]: file || undefined,
    }));
  };

  const progressValue = step === "role" ? 50 : 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to NMTSA Learn
          </h1>
          <p className="text-lg text-gray-600">
            Let&apos;s personalize your learning experience
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              {step === "role"
                ? "Step 1 of 2: Choose Your Role"
                : "Step 2 of 2: Complete Your Profile"}
            </span>
            <span className="text-sm text-gray-500">{progressValue}%</span>
          </div>
          <Progress
            aria-label="Onboarding progress"
            className="w-full"
            color="primary"
            value={progressValue}
          />
        </div>

        {error && (
          <Card className="mb-6 border-2 border-red-200 bg-red-50">
            <CardBody>
              <p className="text-sm text-red-800">{error}</p>
            </CardBody>
          </Card>
        )}

        {/* Step 1: Role Selection */}
        {step === "role" && (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
              How would you like to use NMTSA Learn?
            </h2>

            <div className="grid md:grid-cols-2 gap-4">
              {/* Student Card */}
              <Card
                isPressable
                className="group hover:border-blue-500 hover:shadow-lg transition-all cursor-pointer border-2"
                onClick={() => !isLoading && handleRoleSelect("student")}
              >
                <CardBody className="text-center p-8">
                  <div className="mx-auto w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                    <Users className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">
                    I&apos;m a Student
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    I want to learn about caregiving and neurologic music
                    therapy
                  </p>
                  <div className="flex flex-col gap-2 text-left">
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Access courses and resources</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Track your learning progress</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Earn certificates</span>
                    </div>
                  </div>
                </CardBody>
              </Card>

              {/* Teacher Card */}
              <Card
                isPressable
                className="group hover:border-purple-500 hover:shadow-lg transition-all cursor-pointer border-2"
                onClick={() => !isLoading && handleRoleSelect("teacher")}
              >
                <CardBody className="text-center p-8">
                  <div className="mx-auto w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
                    <GraduationCap className="w-8 h-8 text-purple-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">
                    I&apos;m a Teacher
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    I want to create and share courses with students
                  </p>
                  <div className="flex flex-col gap-2 text-left">
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Create and manage courses</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Share your expertise</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <Check className="w-4 h-4 text-green-600" />
                      <span>Track student progress</span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        )}

        {/* Step 2: Teacher Profile */}
        {step === "profile" && selectedRole === "teacher" && (
          <form className="space-y-6" onSubmit={handleTeacherSubmit}>
            <Card>
              <CardBody className="p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                  Teacher Profile
                </h2>

                <div className="space-y-4">
                  <Input
                    description="Tell students about your professional background"
                    label="Bio"
                    placeholder="I am a certified neurologic music therapist..."
                    value={teacherData.bio}
                    onChange={(e) =>
                      setTeacherData((prev) => ({
                        ...prev,
                        bio: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="List your degrees, certifications, and qualifications"
                    label="Credentials"
                    placeholder="MT-BC, NMT, Bachelor's in Music Therapy..."
                    value={teacherData.credentials}
                    onChange={(e) =>
                      setTeacherData((prev) => ({
                        ...prev,
                        credentials: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="Your area of expertise"
                    label="Specialization"
                    placeholder="Neurologic Music Therapy for Children"
                    value={teacherData.specialization}
                    onChange={(e) =>
                      setTeacherData((prev) => ({
                        ...prev,
                        specialization: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="How many years have you been practicing?"
                    label="Years of Experience"
                    min="0"
                    placeholder="5"
                    type="number"
                    value={teacherData.years_experience?.toString() || ""}
                    onChange={(e) =>
                      setTeacherData((prev) => ({
                        ...prev,
                        years_experience: e.target.value
                          ? parseInt(e.target.value, 10)
                          : undefined,
                      }))
                    }
                  />

                  {/* Resume Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Resume / CV (Optional)
                    </label>
                    <div className="flex items-center gap-4">
                      <Button
                        as="label"
                        className="cursor-pointer"
                        color="default"
                        startContent={<Upload className="w-4 h-4" />}
                        variant="flat"
                      >
                        Choose File
                        <input
                          accept=".pdf,.doc,.docx"
                          className="hidden"
                          type="file"
                          onChange={(e) =>
                            handleFileChange(
                              "resume",
                              e.target.files?.[0] || null,
                            )
                          }
                        />
                      </Button>
                      {teacherData.resume && (
                        <span className="text-sm text-gray-600">
                          {teacherData.resume.name}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      PDF, DOC, or DOCX up to 10MB
                    </p>
                  </div>

                  {/* Certifications Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Certifications (Optional)
                    </label>
                    <div className="flex items-center gap-4">
                      <Button
                        as="label"
                        className="cursor-pointer"
                        color="default"
                        startContent={<Upload className="w-4 h-4" />}
                        variant="flat"
                      >
                        Choose File
                        <input
                          accept=".pdf,.jpg,.jpeg,.png"
                          className="hidden"
                          type="file"
                          onChange={(e) =>
                            handleFileChange(
                              "certifications",
                              e.target.files?.[0] || null,
                            )
                          }
                        />
                      </Button>
                      {teacherData.certifications && (
                        <span className="text-sm text-gray-600">
                          {teacherData.certifications.name}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      PDF, JPG, or PNG up to 10MB
                    </p>
                  </div>
                </div>

                <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>Note:</strong> Your profile will be reviewed by our
                    admin team before you can start creating courses. This
                    typically takes 1-2 business days.
                  </p>
                </div>

                <div className="mt-8 flex gap-4">
                  <Button
                    color="default"
                    variant="flat"
                    onClick={() => {
                      setStep("role");
                      setSelectedRole(null);
                    }}
                  >
                    Back
                  </Button>
                  <Button
                    className="flex-1"
                    color="primary"
                    isLoading={isLoading}
                    type="submit"
                  >
                    Complete Profile
                  </Button>
                </div>
              </CardBody>
            </Card>
          </form>
        )}

        {/* Step 2: Student Profile */}
        {step === "profile" && selectedRole === "student" && (
          <form className="space-y-6" onSubmit={handleStudentSubmit}>
            <Card>
              <CardBody className="p-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                  Student Profile
                </h2>

                <div className="space-y-4">
                  <Select
                    description="Your relationship to the person receiving care"
                    label="I am a..."
                    placeholder="Select your relationship"
                    value={studentData.relationship}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        relationship: e.target.value,
                      }))
                    }
                  >
                    {RELATIONSHIP_CHOICES.map((choice) => (
                      <SelectItem key={choice.value}>{choice.label}</SelectItem>
                    ))}
                  </Select>

                  <Input
                    description="Optional - person receiving care"
                    label="Care Recipient Name"
                    placeholder="John Doe"
                    value={studentData.care_recipient_name}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        care_recipient_name: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="Age of the person receiving care"
                    label="Care Recipient Age"
                    min="0"
                    placeholder="25"
                    type="number"
                    value={studentData.care_recipient_age?.toString() || ""}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        care_recipient_age: e.target.value
                          ? parseInt(e.target.value, 10)
                          : undefined,
                      }))
                    }
                  />

                  <Textarea
                    description="Any special needs, conditions, or considerations"
                    label="Special Needs"
                    placeholder="Autism spectrum disorder, requires visual learning aids..."
                    value={studentData.special_needs || ""}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        special_needs: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="What do you hope to learn or achieve?"
                    label="Learning Goals"
                    placeholder="I want to learn music therapy techniques to help my child..."
                    value={studentData.learning_goals}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        learning_goals: e.target.value,
                      }))
                    }
                  />

                  <Input
                    description="Areas of interest for course recommendations"
                    label="Interests"
                    placeholder="Music therapy for autism, speech development..."
                    value={studentData.interests}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        interests: e.target.value,
                      }))
                    }
                  />

                  <Textarea
                    description="Any accessibility requirements for learning"
                    label="Accessibility Needs"
                    placeholder="Closed captions, screen reader compatible..."
                    value={studentData.accessibility_needs || ""}
                    onChange={(e) =>
                      setStudentData((prev) => ({
                        ...prev,
                        accessibility_needs: e.target.value,
                      }))
                    }
                  />
                </div>

                <div className="mt-8 flex gap-4">
                  <Button
                    color="default"
                    variant="flat"
                    onClick={() => {
                      setStep("role");
                      setSelectedRole(null);
                    }}
                  >
                    Back
                  </Button>
                  <Button
                    className="flex-1"
                    color="primary"
                    isLoading={isLoading}
                    type="submit"
                  >
                    Complete Profile
                  </Button>
                </div>
              </CardBody>
            </Card>
          </form>
        )}
      </div>
    </div>
  );
}
