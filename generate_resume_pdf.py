import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_resume_pdf(output_paths):
    styles = getSampleStyleSheet()
    
    # Custom styles
    name_style = ParagraphStyle(
        'ResumeName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#111827')
    )
    
    contact_style = ParagraphStyle(
        'ResumeContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4B5563')
    )
    
    section_heading_style = ParagraphStyle(
        'ResumeSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=2
    )
    
    body_style = ParagraphStyle(
        'ResumeBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1F2937')
    )
    
    bold_body_style = ParagraphStyle(
        'ResumeBoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#111827')
    )

    right_meta_style = ParagraphStyle(
        'ResumeRightMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#374151')
    )
    
    bullet_style = ParagraphStyle(
        'ResumeBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#374151')
    )

    for output_path in output_paths:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        story = []
        
        # 1. Header: Name & Contact Info
        story.append(Paragraph("Pemmasani Tejaswini", name_style))
        story.append(Spacer(1, 4))
        
        contact_line = (
            'Bangalore, India &nbsp;|&nbsp; '
            '<a href="mailto:pemmasanitejaswini59@gmail.com" color="#2563EB">pemmasanitejaswini59@gmail.com</a> &nbsp;|&nbsp; '
            '+91 8341650531 &nbsp;|&nbsp; '
            '<a href="https://linkedin.com" color="#2563EB">LinkedIn</a> &nbsp;|&nbsp; '
            '<a href="https://github.com/pemmasanitejaswini" color="#2563EB">GitHub</a>'
        )
        story.append(Paragraph(contact_line, contact_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceBefore=0, spaceAfter=8))
        
        # 2. Career Objective
        story.append(Paragraph("CAREER OBJECTIVE", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        obj_text = (
            "To obtain a position as a Software Engineer in a growth-oriented organization where I can apply "
            "my programming knowledge, problem-solving skills, and passion for technology to develop innovative solutions "
            "while continuously learning and contributing to the company’s success."
        )
        story.append(Paragraph(obj_text, body_style))
        story.append(Spacer(1, 7))
        
        # 3. Education
        story.append(Paragraph("EDUCATION", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        
        edu_table_data = [
            [
                Paragraph("<b>B.Tech in Computer Science and Engineering</b><br/><font color='#4B5563'>PBR Vits, Kavali</font>", body_style),
                Paragraph("2022 – 2026<br/><b>CGPA: 8.40</b>", right_meta_style)
            ]
        ]
        edu_table = Table(edu_table_data, colWidths=[380, 160])
        edu_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(edu_table)
        story.append(Spacer(1, 7))
        
        # 4. Internship
        story.append(Paragraph("INTERNSHIP", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        
        intern_table_data = [
            [
                Paragraph("<b>Code Tantra Platform</b>", bold_body_style),
                Paragraph("Python Full Stack Developer Intern (12-5-2025 – 21-06-2025)", right_meta_style)
            ]
        ]
        intern_table = Table(intern_table_data, colWidths=[200, 340])
        intern_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(intern_table)
        story.append(Spacer(1, 3))
        story.append(Paragraph("&bull; Completed a hands-on internship focused on Python and HTML.", bullet_style))
        story.append(Paragraph("&bull; Gained practical experience in programming and web development.", bullet_style))
        story.append(Spacer(1, 7))
        
        # 5. Technical Skills & Soft Skills
        story.append(Paragraph("TECHNICAL SKILLS", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        story.append(Paragraph("<b>&bull; Programming Languages:</b> Python, SQL", bullet_style))
        story.append(Paragraph("<b>&bull; Web Development:</b> HTML, CSS, JS", bullet_style))
        story.append(Paragraph("<b>&bull; Libraries & Tools:</b> OpenCV", bullet_style))
        story.append(Spacer(1, 7))
        
        story.append(Paragraph("SOFT SKILLS", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        story.append(Paragraph("&bull; Communication skills &nbsp;|&nbsp; &bull; Adaptability &nbsp;|&nbsp; &bull; Time management &nbsp;|&nbsp; &bull; Problem solving", bullet_style))
        story.append(Spacer(1, 7))
        
        # 6. Projects
        story.append(Paragraph("PROJECTS", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        
        # Project 1: Face Recognition Attendance System
        p1_table_data = [
            [
                Paragraph("<b>Face Recognition Attendance System</b>", bold_body_style),
                Paragraph('<a href="https://github.com/pemmasanitejaswini/face-project" color="#2563EB"><i>GitHub Repo &nearr;</i></a>', right_meta_style)
            ]
        ]
        p1_table = Table(p1_table_data, colWidths=[380, 160])
        p1_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(p1_table)
        story.append(Paragraph("&bull; Developed a system for real-time face detection and recognition through a webcam using OpenCV and Python.", bullet_style))
        story.append(Paragraph("&bull; Automated the attendance marking process to reduce manual effort and prevent proxy attendance.", bullet_style))
        story.append(Paragraph("&bull; <b>Technologies Used:</b> Python, OpenCV, Face Recognition, MySQL", bullet_style))
        story.append(Spacer(1, 6))
        
        # Project 2: Email Spam Detection
        p2_table_data = [
            [
                Paragraph("<b>Email Spam Detection</b>", bold_body_style),
                Paragraph('<a href="https://github.com/pemmasanitejaswini/email-spam-detection" color="#2563EB"><i>GitHub Repo &nearr;</i></a>', right_meta_style)
            ]
        ]
        p2_table = Table(p2_table_data, colWidths=[380, 160])
        p2_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(p2_table)
        story.append(Paragraph("&bull; Built a Machine Learning model to classify emails as Spam or Not Spam based on email content analysis.", bullet_style))
        story.append(Paragraph("&bull; Implemented Natural Language Processing techniques to pre-process text data and improve prediction accuracy.", bullet_style))
        story.append(Paragraph("&bull; <b>Technologies Used:</b> Python, Scikit-Learn, NLP, Flask/FastAPI", bullet_style))
        story.append(Spacer(1, 6))
        
        # Project 3: CAPTCHA Generator
        p3_table_data = [
            [
                Paragraph("<b>CAPTCHA Generator</b>", bold_body_style),
                Paragraph('<a href="https://github.com/pemmasanitejaswini/captcha-generator" color="#2563EB"><i>GitHub Repo &nearr;</i></a>', right_meta_style)
            ]
        ]
        p3_table = Table(p3_table_data, colWidths=[380, 160])
        p3_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(p3_table)
        story.append(Paragraph("&bull; Developed a dynamic CAPTCHA generator to enhance web application security by preventing automated bot scripts.", bullet_style))
        story.append(Paragraph("&bull; Designed a user-friendly interface to display visual verification codes with custom noise and fonts.", bullet_style))
        story.append(Paragraph("&bull; <b>Technologies Used:</b> Python, HTML, Web Technologies", bullet_style))
        story.append(Spacer(1, 7))
        
        # 7. Certifications & Achievements
        story.append(Paragraph("CERTIFICATIONS & ACHIEVEMENTS", section_heading_style))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor('#CBD5E1'), spaceBefore=1, spaceAfter=5))
        story.append(Paragraph("<b>&bull; Paper Presentation:</b> Received participation certificate at PBR VITS College during the event Visvotsav 2024.", bullet_style))
        story.append(Paragraph("<b>&bull; Debugging Event:</b> Received Participation Certificate in Debugging Event conducted at Andhra Engineering College, Atmakur.", bullet_style))
        
        doc.build(story)
        print(f"Generated PDF: {output_path} (Size: {os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    targets = [
        "resume.pdf",
        "Tejaswini_Pemmasani_Resume.pdf"
    ]
    build_resume_pdf(targets)
