import type { DashboardStats as StatsType } from "../../types/api";

import { Card, CardBody } from "@heroui/card";
import { useTranslation } from "react-i18next";
import {
  BookOpen,
  CheckCircle,
  Clock,
  Award,
  TrendingUp,
  Flame,
} from "lucide-react";

interface DashboardStatsProps {
  stats: StatsType;
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  const { t } = useTranslation();

  const statCards = [
    {
      icon: BookOpen,
      label: t("dashboard.totalCourses"),
      value: stats.totalCourses,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      icon: Clock,
      label: t("dashboard.inProgress"),
      value: stats.inProgressCourses,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      icon: CheckCircle,
      label: t("dashboard.completed"),
      value: stats.completedCourses,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      icon: Award,
      label: t("dashboard.certificates"),
      value: stats.totalCertificates,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      icon: TrendingUp,
      label: t("dashboard.learningHours"),
      value: Math.round(stats.totalLearningHours),
      suffix: "h",
      color: "text-indigo-600",
      bgColor: "bg-indigo-50",
    },
    {
      icon: Flame,
      label: t("dashboard.currentStreak"),
      value: stats.currentStreak,
      suffix: t("dashboard.days"),
      color: "text-red-600",
      bgColor: "bg-red-50",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {statCards.map((stat, index) => {
        const Icon = stat.icon;

        return (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardBody className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {stat.value}
                    {stat.suffix && (
                      <span className="text-lg text-gray-600 ml-1">
                        {stat.suffix}
                      </span>
                    )}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
}
