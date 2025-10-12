import skills from "@/data/skills.json";
import projects from "@/data/projects.json";
import education from "@/data/education.json";
import work from "@/data/work.json";
import achievements from "@/data/achievements.json";
import contact from "@/data/contact.json";

export interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export const getSimulatedResponse = (userMessage: string): string => {
  const lowerCaseMessage = userMessage.toLowerCase();

  if (
    lowerCaseMessage.includes("hello") ||
    lowerCaseMessage.includes("hi") ||
    lowerCaseMessage.includes("hey")
  ) {
    return "Hello there! How can I help you today? Feel free to ask about my skills, projects, education, or work experience.";
  } else if (
    lowerCaseMessage.includes("skill") ||
    lowerCaseMessage.includes("technology") ||
    lowerCaseMessage.includes("tech stack")
  ) {
    // Group skills by category
    const skillsByCategory: Record<string, string[]> = {};
    skills.forEach((skill) => {
      if (!skillsByCategory[skill.category]) {
        skillsByCategory[skill.category] = [];
      }
      skillsByCategory[skill.category].push(skill.name);
    });
    let response = `Here are some of my key skills:\n\n`;
    Object.entries(skillsByCategory).forEach(([category, skillNames]) => {
      response += `• **${category}**: ${skillNames.join(", ")}\n\n`;
    });
    response += `\nFeel free to ask for more details about any specific technology!`;
    return response;
  } else if (
    lowerCaseMessage.includes("project") ||
    lowerCaseMessage.includes("portfolio")
  ) {
    let response = `I've worked on various projects including:\n\n`;
    // Get the first 4 projects to keep the response concise
    const highlightedProjects = projects.slice(0, 4);
    highlightedProjects.forEach((project) => {
      response += `• **${project.name}**: ${project.shortDescription}\n\n`;
    });
    response += `\nYou can find more details in the Projects section of my portfolio or at [my GitHub](${contact.github}).`;
    return response;
  } else if (
    lowerCaseMessage.includes("contact") ||
    lowerCaseMessage.includes("email") ||
    lowerCaseMessage.includes("reach")
  ) {
    return `You can reach me through:\n\n• Email: ${contact.email}\n\n• GitHub: ${contact.github}\n\n• LinkedIn: ${contact.linkedin}\n\n• Devpost: ${contact.devpost}\n\nI look forward to connecting with you!`;
  } else if (
    lowerCaseMessage.includes("experience") ||
    lowerCaseMessage.includes("work") ||
    lowerCaseMessage.includes("job")
  ) {
    let response = `My professional experience includes:\n\n`;
    work.forEach((job) => {
      const endDate = job.endDate || "Present";
      const duration =
        job.startDate.split("-")[0] + "-" + endDate.split("-")[0];
      response += `• **${job.position}** at ${job.company} (${duration})\n\n`;
    });
    response += `\nI've worked on software feature creation, deployment, data pipelines, and mentoring students.`;
    return response;
  } else if (
    lowerCaseMessage.includes("education") ||
    lowerCaseMessage.includes("degree") ||
    lowerCaseMessage.includes("university")
  ) {
    let response = `My educational background:\n\n`;
    education.forEach((edu) => {
      response += `• **${edu.degree} in ${edu.field}** - ${edu.institution} (${edu.startDate}-${edu.endDate || "Present"})\n  GPA: ${edu.gpa}/4.0\n\n`;
    });
    const courses = education
      .flatMap((edu) => edu.subjects.map((s) => s.name))
      .slice(0, 3);
    response += `\nI've completed coursework in ${courses.join(", ")}, and more.`;
    return response;
  } else if (
    lowerCaseMessage.includes("achievement") ||
    lowerCaseMessage.includes("award") ||
    lowerCaseMessage.includes("recognition")
  ) {
    let response = `Some of my notable achievements include:\n\n`;
    achievements.forEach((achievement) => {
      response += `• **${achievement.title}** - ${achievement.description}\n\n`;
    });
    return response;
  } else if (
    lowerCaseMessage.includes("about") ||
    lowerCaseMessage.includes("who") ||
    lowerCaseMessage.includes("background")
  ) {
    const currentJob = work[0].position;
    const currentCompany = work[0].company;
    const edu = `${education[0].degree} in ${education[0].field}`;
    const university = education[0].institution;

    return `I am Aakash Khepar, a passionate software developer with expertise in full-stack development. I enjoy creating efficient, user-friendly applications and solving complex problems.

My journey includes working as a ${currentJob} at ${currentCompany}, contributing to multiple projects, and continuously expanding my technical knowledge. I'm currently pursuing a ${edu} at ${university}.

Feel free to ask more specific questions about my skills, projects, or experience!`;
  } else {
    return `Thanks for your question! Here are some topics you might be interested in:

• My skills and technologies
• Projects I've worked on
• Work experience
• Educational background
• Contact information

Feel free to ask about any of these topics for more information!`;
  }
};
